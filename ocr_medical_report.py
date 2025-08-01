from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import time
import json
import re

# Initialize the OCR model with specific architectures
model = ocr_predictor(det_arch='fast_base', reco_arch='crnn_mobilenet_v3_small', pretrained=True).to('cpu')

# Load document
doc = DocumentFile.from_images("test4.jpg")

start_time = time.time()
# Analyze
result = model(doc)
print("Inference time: ", time.time() - start_time)

# Get JSON output for structured processing
json_output = result.export()

# Extract just the plain text in reading order
print("\n" + "="*50)
print("PLAIN TEXT OUTPUT")
print("="*50)

def extract_plain_text(json_data):
    """Extract plain text in reading order"""
    full_text = []
    
    for page in json_data.get("pages", []):
        page_text = []
        for block in page.get("blocks", []):
            block_text = []
            for line in block.get("lines", []):
                line_words = [word.get("value", "") for word in line.get("words", [])]
                if line_words:
                    block_text.append(" ".join(line_words))
            if block_text:
                page_text.append("\n".join(block_text))
        if page_text:
            full_text.append("\n\n".join(page_text))
    
    return "\n\n".join(full_text)

plain_text = extract_plain_text(json_output)
print(plain_text)

def extract_structured_medical_data(json_data):
    """Extract structured medical data from OCR results"""
    medical_data = {
        "report_title": "",
        "tests": [],
        "comments": [],
        "metadata": {}
    }
    
    # Extract all text lines for processing
    all_lines = []
    for page in json_data.get("pages", []):
        for block in page.get("blocks", []):
            for line in block.get("lines", []):
                line_text = " ".join([word.get("value", "") for word in line.get("words", [])])
                if line_text.strip():
                    all_lines.append(line_text.strip())
    
    # Find report title (usually first line or contains "Analysis")
    for line in all_lines[:5]:  # Check first 5 lines
        if "analysis" in line.lower() or "hormon" in line.lower():
            medical_data["report_title"] = line
            break
    
    # Extract test results using pattern matching
    test_patterns = [
        r'(\w+)\s+([\d\.]+(?:\s*[Hh])?)\s+([^\s]+)\s+([^\s]+)\s+([\d\.\s\-]+)',
        r'(\w+)\s+([\d\.]+(?:\s*[Hh])?)\s+([^\s]+)\s+([\d\.\s\-]+)',
    ]
    
    for line in all_lines:
        line_lower = line.lower()
        
        # Skip header lines and empty lines
        if any(header in line_lower for header in ['test', 'result', 'unit', 'method', 'normal']):
            continue
            
        # Try to match test result patterns
        for pattern in test_patterns:
            matches = re.findall(pattern, line)
            if matches:
                for match in matches:
                    if len(match) >= 4:
                        test_name = match[0].strip()
                        result_value = match[1].strip()
                        unit = match[2].strip() if len(match) > 2 else ""
                        method_or_range = match[3].strip() if len(match) > 3 else ""
                        normal_range = match[4].strip() if len(match) > 4 else ""
                        
                        # Determine if it's a method or normal range
                        if "normal" in line_lower or "-" in method_or_range:
                            normal_range = method_or_range
                            method = ""
                        else:
                            method = method_or_range
                            normal_range = match[4].strip() if len(match) > 4 else ""
                        
                        # Check if result is high/low
                        is_abnormal = "h" in result_value.lower() or "l" in result_value.lower()
                        
                        test_data = {
                            "test_name": test_name,
                            "result": result_value,
                            "unit": unit,
                            "method": method,
                            "normal_range": normal_range,
                            "is_abnormal": is_abnormal
                        }
                        
                        # Avoid duplicates
                        if not any(t["test_name"] == test_name for t in medical_data["tests"]):
                            medical_data["tests"].append(test_data)
        
        # Extract comments (Persian text or medical recommendations)
        if any(keyword in line_lower for keyword in ['توصیه', 'recommend', 'comment', 'note']):
            medical_data["comments"].append(line)
    
    # Extract metadata
    for line in all_lines:
        line_lower = line.lower()
        if "checked by" in line_lower:
            medical_data["metadata"]["checked_by"] = line
        elif "eci" in line_lower or "electrochemiluminescence" in line_lower:
            medical_data["metadata"]["methodology"] = line
    
    return medical_data

# Extract structured medical data
print("\n" + "="*50)
print("STRUCTURED MEDICAL DATA")
print("="*50)

structured_data = extract_structured_medical_data(json_output)
print(json.dumps(structured_data, indent=2, ensure_ascii=False))