"""LLM interaction utilities for knowledge graph generation."""
import re
import json
import time
import random
import requests
from itertools import cycle
from threading import Lock


class APIKeyManager:
    """
    Manages multiple API keys with round-robin rotation and automatic switching on rate limits.
    
    Features:
    - Round-robin key rotation for load distribution
    - Automatic key switching on 429 errors
    - Per-key cooldown tracking
    - Thread-safe operations
    """
    
    def __init__(self, api_keys, cooldown_time=60):
        """
        Initialize the API key manager.
        
        Args:
            api_keys: List of API keys or single API key string
            cooldown_time: Time in seconds to wait before reusing a rate-limited key
        """
        # Handle both single key (backward compatibility) and multiple keys
        if isinstance(api_keys, str):
            api_keys = [api_keys]
        
        if not api_keys or not any(key.strip() for key in api_keys):
            raise ValueError("At least one valid API key must be provided")
        
        # Filter out empty keys and strip whitespace
        self.api_keys = [key.strip() for key in api_keys if key.strip()]
        
        if len(self.api_keys) == 0:
            raise ValueError("No valid API keys found after filtering")
        
        # Create a round-robin iterator
        self.key_cycle = cycle(self.api_keys)
        
        # Track cooldown status for each key: {key: cooldown_until_timestamp}
        self.key_cooldowns = {key: 0 for key in self.api_keys}
        
        # Track usage statistics
        self.key_usage_count = {key: 0 for key in self.api_keys}
        self.key_error_count = {key: 0 for key in self.api_keys}
        
        # Default cooldown time
        self.cooldown_time = cooldown_time
        
        # Thread lock for thread-safe operations
        self.lock = Lock()
        
        print(f"🔑 API Key Manager initialized with {len(self.api_keys)} key(s)")
    
    def get_next_available_key(self):
        """
        Get the next available API key that is not in cooldown.
        
        Returns:
            A tuple of (api_key, key_index) or (None, None) if all keys are in cooldown
        """
        with self.lock:
            current_time = time.time()
            attempts = 0
            max_attempts = len(self.api_keys)
            
            # Try to find an available key
            while attempts < max_attempts:
                key = next(self.key_cycle)
                key_index = self.api_keys.index(key)
                
                # Check if key is not in cooldown
                if self.key_cooldowns[key] <= current_time:
                    self.key_usage_count[key] += 1
                    return key, key_index
                
                attempts += 1
            
            # All keys are in cooldown - find the one with shortest remaining cooldown
            min_cooldown_key = min(self.key_cooldowns.items(), key=lambda x: x[1])
            wait_time = max(0, min_cooldown_key[1] - current_time)
            
            return None, wait_time
    
    def mark_key_rate_limited(self, api_key, retry_after=None):
        """
        Mark a key as rate-limited and put it in cooldown.
        
        Args:
            api_key: The API key that was rate-limited
            retry_after: Optional retry-after time from response headers (in seconds)
        """
        with self.lock:
            # Use retry_after if provided, otherwise use default cooldown
            cooldown = retry_after if retry_after else self.cooldown_time
            
            # Add some jitter (0-20% of cooldown time) to avoid thundering herd
            jitter = random.uniform(0, cooldown * 0.2)
            total_cooldown = cooldown + jitter
            
            self.key_cooldowns[api_key] = time.time() + total_cooldown
            self.key_error_count[api_key] += 1
            
            key_index = self.api_keys.index(api_key) + 1
            print(f"⚠️  API Key #{key_index} rate limited. Cooling down for {total_cooldown:.1f}s")
    
    def get_statistics(self):
        """Get usage statistics for all keys."""
        with self.lock:
            stats = []
            for i, key in enumerate(self.api_keys, 1):
                # Mask the key for security (show first 8 and last 4 chars)
                masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
                stats.append({
                    'key_number': i,
                    'masked_key': masked_key,
                    'usage_count': self.key_usage_count[key],
                    'error_count': self.key_error_count[key],
                    'currently_available': self.key_cooldowns[key] <= time.time()
                })
            return stats


class LLM:
    """Enhanced LLM class with API key rotation support."""
    
    def __init__(self, config):
        self.set_config(config)
    
    def set_config(self, config):
        """
        Set configuration including API key manager.
        
        Args:
            config: Configuration dictionary
        """
        self.model = config["llm"]["model"]
        
        # Initialize API key manager
        api_keys = config["llm"]["api_key"]
        # Support both single key (string) and multiple keys (list)
        if not isinstance(api_keys, list):
            api_keys = [api_keys]
        
        self.key_manager = APIKeyManager(
            api_keys,
            cooldown_time=config["llm"].get("key_cooldown_time", 60)
        )
        
        self.max_tokens = config["llm"]["max_tokens"]
        self.temperature = config["llm"]["temperature"]
        self.base_url = config["llm"]["base_url"]

    def __call__(self, system_prompt, user_prompt):
        return call_llm(
            self.model, user_prompt, self.key_manager, system_prompt,
            self.max_tokens, self.temperature, self.base_url,
        )


def call_llm(model, user_prompt, key_manager, system_prompt=None, 
             max_tokens=1000, temperature=0.2, base_url=None) -> str:
    """
    Call the language model API with automatic key rotation on rate limits.
    
    Args:
        model: The model name to use
        user_prompt: The user prompt to send
        key_manager: APIKeyManager instance for handling multiple keys
        system_prompt: Optional system prompt to set context
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature
        base_url: The base URL for the API endpoint
        
    Returns:
        The model's response as a string
    """
    
    messages = []
    
    if system_prompt:
        messages.append({
            'role': 'system',
            'content': system_prompt
        })
    
    messages.append({
        'role': 'user',
        'content': [
            {
                'type': 'text',
                'text': user_prompt
            }
        ]
    })
    
    payload = {
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': temperature
    }
    
    max_retries = 15  # Increased retries to handle key rotation
    base_retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        # Get next available API key
        api_key, wait_or_index = key_manager.get_next_available_key()
        
        # If all keys are in cooldown, wait for the shortest cooldown
        if api_key is None:
            wait_time = wait_or_index
            if wait_time > 0:
                jitter = random.uniform(0.5, 2.5)
                total_wait = wait_time + jitter
                print(f"⏳ All API keys in cooldown. Waiting {total_wait:.1f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(total_wait)
                continue
        
        # Prepare headers with current API key
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {api_key}"
        }
        
        # Add small delay between requests to avoid hammering (0.5-2.5s)
        if attempt > 0:
            jitter = random.uniform(0.5, 2.5)
            time.sleep(jitter)
        
        try:
            response = requests.post(
                base_url,
                headers=headers,
                json=payload,
                timeout=120  # 2 minute timeout
            )
            
            # Success - parse and return
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    
                    # Validate response structure
                    if 'choices' not in response_json:
                        print(f"⚠️  Warning: Response missing 'choices' field")
                        raise KeyError("'choices' not found in response")
                    
                    if len(response_json['choices']) == 0:
                        print(f"⚠️  Warning: Response has empty 'choices' array")
                        raise KeyError("'choices' array is empty")
                    
                    message = response_json['choices'][0].get('message', {})
                    
                    if 'content' not in message:
                        print(f"⚠️  Warning: Message missing 'content' field")
                        
                        # Try alternative fields
                        if 'text' in message:
                            print("✅ Found 'text' field instead of 'content'")
                            return message['text']
                        
                        raise KeyError("'content' not found in message")
                    
                    return message['content']
                    
                except (KeyError, IndexError, TypeError) as e:
                    print(f"❌ Error parsing response: {e}")
                    
                    # Retry with exponential backoff for parsing errors
                    if attempt < max_retries - 1:
                        wait_time = base_retry_delay * (2 ** attempt)
                        jitter = random.uniform(0, wait_time * 0.2)
                        total_wait = wait_time + jitter
                        print(f"🔄 Malformed response, waiting {total_wait:.1f}s before retry {attempt + 2}/{max_retries}...")
                        time.sleep(total_wait)
                        continue
                    else:
                        raise Exception(f"API response parsing failed after {max_retries} retries: {e}")
            
            # Rate limit hit - mark key as rate-limited and try next key
            elif response.status_code == 429:
                # Try to extract retry-after time from response
                retry_after = None
                try:
                    error_data = response.json()
                    if 'error' in error_data and 'details' in error_data['error']:
                        for detail in error_data['error']['details']:
                            if detail.get('@type') == 'type.googleapis.com/google.rpc.RetryInfo':
                                retry_info = detail.get('retryDelay', '')
                                if retry_info:
                                    # Parse retry delay (format: "26s" or "26.400891299s")
                                    retry_after = float(retry_info.rstrip('s')) + 1  # Add 1s buffer
                                break
                except:
                    pass
                
                # Mark this key as rate-limited
                key_manager.mark_key_rate_limited(api_key, retry_after)
                
                # Continue to next iteration to try another key
                if attempt < max_retries - 1:
                    print(f"🔄 Switching to next API key (attempt {attempt + 2}/{max_retries})...")
                    continue
                else:
                    raise Exception(f"All API keys exhausted after {max_retries} retries (rate limits)")
            
            # Server errors (503, 500, 502, 504) - retry with backoff
            elif response.status_code >= 500:
                if attempt < max_retries - 1:
                    wait_time = base_retry_delay * (2 ** attempt)
                    jitter = random.uniform(0, wait_time * 0.2)
                    total_wait = wait_time + jitter
                    print(f"❌ Server error ({response.status_code}), waiting {total_wait:.1f}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(total_wait)
                    continue
                else:
                    raise Exception(f"API request failed after {max_retries} retries (server error): {response.text}")
            
            # Client errors (4xx other than 429) - don't retry
            else:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
        
        except requests.exceptions.Timeout:
            print(f"⏱️  Request timeout. Retrying with next key ({attempt + 2}/{max_retries})...")
            if attempt < max_retries - 1:
                continue
            else:
                raise Exception(f"API request timed out after {max_retries} retries")
        
        except requests.exceptions.RequestException as e:
            print(f"🌐 Network error: {e}. Retrying ({attempt + 2}/{max_retries})...")
            if attempt < max_retries - 1:
                time.sleep(base_retry_delay)
                continue
            else:
                raise Exception(f"API request failed after {max_retries} retries: {e}")
    
    # Should not reach here, but just in case
    raise Exception(f"API request failed after {max_retries} retries")

def extract_json_from_text(text, verbose=True):
    """
    Extract JSON array from text that might contain additional content.

    Args:
        text: Text that may contain JSON

    Returns:
        The parsed JSON if found, None otherwise
    """
    # First, check if the text is wrapped in code blocks with triple backticks
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    code_match = re.search(code_block_pattern, text)
    if code_match:
        text = code_match.group(1).strip()
        if verbose:
            print("Found JSON in code block, extracting content...")

    try:
        # Try direct parsing in case the response is already clean JSON
        return json.loads(text)
    except json.JSONDecodeError:
        # Look for opening and closing brackets of a JSON array
        start_idx = text.find('[')
        if start_idx == -1:
            print("No JSON array start found in text")
            return None

        # Simple bracket counting to find matching closing bracket
        bracket_count = 0
        complete_json = False
        for i in range(start_idx, len(text)):
            if text[i] == '[':
                bracket_count += 1
            elif text[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    # Found the matching closing bracket
                    json_str = text[start_idx:i+1]
                    complete_json = True
                    break

        # Handle complete JSON array
        if complete_json:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print("Found JSON-like structure but couldn't parse it.")
                print("Trying to fix common formatting issues...")

                # Try to fix missing quotes around keys
                fixed_json = re.sub(r'(\s*)(\w+)(\s*):(\s*)', r'\1"\2"\3:\4', json_str)
                # Fix trailing commas
                fixed_json = re.sub(r',(\s*[\]}])', r'\1', fixed_json)

                try:
                    return json.loads(fixed_json)
                except:
                    print("Could not fix JSON format issues")
        else:
            # Handle incomplete JSON - try to complete it
            print("Found incomplete JSON array, attempting to complete it...")

            # Get all complete objects from the array
            objects = []
            obj_start = -1
            obj_end = -1
            brace_count = 0

            # First find all complete objects
            for i in range(start_idx + 1, len(text)):
                if text[i] == '{':
                    if brace_count == 0:
                        obj_start = i
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        obj_end = i
                        objects.append(text[obj_start:obj_end+1])

            if objects:
                # Reconstruct a valid JSON array with complete objects
                reconstructed_json = "[\n" + ",\n".join(objects) + "\n]"
                try:
                    return json.loads(reconstructed_json)
                except json.JSONDecodeError:
                    print("Couldn't parse reconstructed JSON array.")
                    print("Trying to fix common formatting issues...")

                    # Try to fix missing quotes around keys
                    fixed_json = re.sub(r'(\s*)(\w+)(\s*):(\s*)', r'\1"\2"\3:\4', reconstructed_json)
                    # Fix trailing commas
                    fixed_json = re.sub(r',(\s*[\]}])', r'\1', fixed_json)

                    try:
                        return json.loads(fixed_json)
                    except:
                        print("Could not fix JSON format issues in reconstructed array")

        print("No complete JSON array could be extracted")
        return None