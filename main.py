from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# 🔒 सुरक्षित पद्धत: कोडमधून खरी API Key काढून टाकली आहे.
# रेंडर सर्व्हर ही की (Key) त्याच्या Environment Variables मधून आपोआप वाचेल.
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GENAI_API_KEY:
    # जर रेंडरवर की सेट नसेल, तर तात्पुरती एरर दाखवेल
    raise RuntimeWarning("GEMINI_API_KEY environment variable is missing!")

genai.configure(api_key=GENAI_API_KEY)

class AnalysisRequest(BaseModel):
    video_url: str
    language: str

@app.post("/api/v1/analyze")
async def analyze_video(request: AnalysisRequest):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        तू एक अत्यंत प्रगत एआय संशोधन (AI Research Engine) आणि फॅक्ट-चेकर (Fact Checker) इंजीन आहेस.
        तुला या व्हिडिओची लिंक दिली आहे: {request.video_url}
        
        तुझे काम या व्हिडिओचे सखोल विश्लेषण करून खालील मुद्द्यांनुसार अत्यंत अचूक माहिती {request.language} भाषेत देणे हे आहे. रिपोर्टचे स्वरूप व्यावसायिक असावे:
        
        📊 **भाग १: सखोल संशोधन अहवाल (Comprehensive Research Report)**
        - **मुख्य विषय (Core Topic):** हा व्हिडिओ नक्की कोणत्या विषयावर आहे आणि त्याचे महत्त्व काय आहे?
        - **सखोल विश्लेषण (In-depth Analysis):** या विषयाची पार्श्वभूमी काय आहे? बाजारपेठेतील चालू घडामोडी, ट्रेंड्स किंवा तांत्रिक बाजू काय सांगतात?
        - **महत्त्वाची आकडेवारी (Key Data & Statistics):** या विषयाशी संबंधित उपलब्ध असलेली महत्त्वाची आकडेवारी किंवा तथ्ये स्पष्ट करा.
        
        🗣️ **भाग २: व्हिडिओमधील अचूक संभाषण व हेतू (Transcript & Intent Analysis)**
        - **संभाषणाचा सारांश (Exact Dialogue Analysis):** व्हिडिओमध्ये नक्की काय बोलले गेले आहे? मुख्य व्यक्तीने कोणते विशिष्ट मुद्दे मांडले आहेत? (व्हिडिओला सबटायटल्स नसतील, तरी विषयानुसार संभाषणाचा अचूक गाभा द्या).
        - **मुख्य शब्द (Keywords):** वक्त्याने कोणते महत्त्वाचे शब्द वारंवार वापरले आहेत?
        - **हेतू (Intent):** वक्त्याचा हा व्हिडिओ बनवण्यामागचा खरा हेतू (उदा. प्रबोधन, जाहिरात, मतप्रदर्शन, अफवा पसरवणे) काय आहे?
        
        🔍 **भाग ३: सत्यता पडताळणी (Strict Fact Check)**
        - **दावे विरुद्ध वास्तव (Claims vs Reality):** व्हिडिओमध्ये जे काही मोठे दावे (Claims) केले गेले आहेत, यांची यादी करा.
        - **सत्यता पडताळणी (Fact Check Verdict):** इंटरनेटवरील उपलब्ध डेटा, अधिकृत सरकारी रिपोर्ट्स किंवा जागतिक माहितीच्या आधारे हे दावे तपासा. प्रत्येक दाव्यासमोर स्पष्टपणे 'सत्य (True)', 'अर्धसत्य (Partially True)' किंवा 'भ्रामक/अफवा (False/Misleading)' असे ठळकपणे लिहा आणि त्याचे कारण द्या.
        
        🎯 **भाग ४: अंतिम निष्कर्ष आणि सल्ला (Final Verdict & Recommendations)**
        - हा व्हिडिओ आणि यातील माहिती किती विश्वासार्ह आहे? वापरकर्त्याने या माहितीचा वापर कसा करावा आणि कोणती काळजी घ्यावी?
        
        माहिती अत्यंत मुद्देसूद, स्पष्ट आणि आकर्षक फॉरमॅटमध्ये (Bullet Points आणि Bold Text वापरून) असावी. कोणतीही मनाची किंवा खोटी माहिती जोडू नकोस.
        """
        
        response = model.generate_content(prompt)
        
        if response.text:
            return {
                "status": "success",
                "report": response.text
            }
        else:
            raise HTTPException(status_code=500, detail="AI रिसर्च रिपोर्ट तयार करू शकला नाही.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
