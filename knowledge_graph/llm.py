"""LLM interaction utilities for knowledge graph generation."""
import requests
import json
import re

def call_llm(model, user_prompt, api_key, system_prompt=None, max_tokens=1000, temperature=0.2, base_url=None) -> str:
    """
    Call the language model API.
    
    Args:
        model: The model name to use
        user_prompt: The user prompt to send
        api_key: The API key for authentication
        system_prompt: Optional system prompt to set context
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature
        base_url: The base URL for the API endpoint
        
    Returns:
        The model's response as a string
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {api_key}"
    }
    
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
    
    import time
    import random
    
    max_retries = 10  # Tăng số lần retry
    base_retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        # Thêm delay nhỏ giữa các requests để tránh rate limit
        if attempt > 0:
            # Thêm random jitter (0.5-2.5s) để tránh thundering herd
            jitter = random.uniform(0.5, 2.5)
            time.sleep(2 + jitter)
        
        response = requests.post(
            base_url,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                
                # Kiểm tra cấu trúc response
                if 'choices' not in response_json:
                    print(f"⚠️  Warning: Response missing 'choices' field")
                    print(f"Response: {response_json}")
                    raise KeyError("'choices' not found in response")
                
                if len(response_json['choices']) == 0:
                    print(f"⚠️  Warning: Response has empty 'choices' array")
                    print(f"Response: {response_json}")
                    raise KeyError("'choices' array is empty")
                
                message = response_json['choices'][0].get('message', {})
                
                if 'content' not in message:
                    print(f"⚠️  Warning: Message missing 'content' field")
                    print(f"Full response: {response_json}")
                    
                    # Thử các trường khác có thể chứa content
                    if 'text' in message:
                        print("✅ Found 'text' field instead of 'content'")
                        return message['text']
                    
                    raise KeyError("'content' not found in message")
                
                return message['content']
                
            except (KeyError, IndexError, TypeError) as e:
                print(f"❌ Error parsing response: {e}")
                print(f"Full response status: {response.status_code}")
                print(f"Full response text: {response.text[:500]}...")  # First 500 chars
                
                # Retry với lỗi này
                if attempt < max_retries - 1:
                    wait_time = base_retry_delay * (2 ** attempt)
                    jitter = random.uniform(0, wait_time * 0.2)
                    total_wait = wait_time + jitter
                    print(f"🔄 Malformed response, waiting {total_wait:.1f}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(total_wait)
                    continue  # Retry
                else:
                    raise Exception(f"API response parsing failed after {max_retries} retries: {e}")
        elif response.status_code == 429:  # Rate limit
            if attempt < max_retries - 1:
                # Thử parse retryDelay từ response
                try:
                    error_data = response.json()
                    retry_info = None
                    if 'error' in error_data and 'details' in error_data['error']:
                        for detail in error_data['error']['details']:
                            if detail.get('@type') == 'type.googleapis.com/google.rpc.RetryInfo':
                                retry_info = detail.get('retryDelay', '')
                                break
                    
                    # Parse retry delay (format: "26s" hoặc "26.400891299s")
                    if retry_info:
                        wait_time = float(retry_info.rstrip('s')) + 1  # Thêm 1s buffer
                    else:
                        wait_time = base_retry_delay * (2 ** attempt)  # Exponential backoff
                except:
                    wait_time = base_retry_delay * (2 ** attempt)  # Exponential backoff
                
                # Thêm random jitter để tránh nhiều requests retry cùng lúc
                jitter = random.uniform(0, wait_time * 0.1)  # 0-10% của wait_time
                total_wait = wait_time + jitter
                
                print(f"⚠️  Rate limit hit, waiting {total_wait:.1f} seconds before retry {attempt + 2}/{max_retries}...")
                time.sleep(total_wait)
            else:
                raise Exception(f"API request failed after {max_retries} retries: {response.text}")
        elif response.status_code == 503:  # Service Unavailable (server quá tải)
            if attempt < max_retries - 1:
                # Exponential backoff cho lỗi server quá tải
                wait_time = base_retry_delay * (2 ** attempt)  # 5s, 10s, 20s, 40s...
                jitter = random.uniform(0, wait_time * 0.2)  # 0-20% jitter cho server errors
                total_wait = wait_time + jitter
                print(f"🔄 Server overloaded (503), waiting {total_wait:.1f} seconds before retry {attempt + 2}/{max_retries}...")
                time.sleep(total_wait)
            else:
                raise Exception(f"API request failed after {max_retries} retries (server overloaded): {response.text}")
        elif response.status_code >= 500:  # Các lỗi server khác (500, 502, 504...)
            if attempt < max_retries - 1:
                wait_time = base_retry_delay * (2 ** attempt)
                jitter = random.uniform(0, wait_time * 0.2)  # 0-20% jitter cho server errors
                total_wait = wait_time + jitter
                print(f"❌ Server error ({response.status_code}), waiting {total_wait:.1f} seconds before retry {attempt + 2}/{max_retries}...")
                time.sleep(total_wait)
            else:
                raise Exception(f"API request failed after {max_retries} retries (server error): {response.text}")
        else:
            # Lỗi client (4xx ngoại trừ 429) - không retry
            raise Exception(f"API request failed: {response.text}")

def extract_json_from_text(text):
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