import streamlit as st
import requests
import json
import math

st.set_page_config(page_title="Myanmar TTS & SRT", page_icon="🎙️")
st.title("🎙️ Myanmar TTS & SRT Generator")
st.info("👑 ကြော်ငြာပါ၊ အချိန်စောင့်စရာမလိုဘဲ အကန့်အသတ်မရှိ သုံးချင်ပါက VIP ဝယ်ယူရန် နှိပ်ပါ။")

user_text = st.text_area("မြန်မာစာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ -", height=200, placeholder="ဒီမှာ မြန်မာစာ ရိုက်ထည့်ပါ...")

# စာလုံးရေနှင့် အချိန် တွက်ချက်ခြင်း
if user_text:
    char_count = len(user_text)
    word_count = len(user_text.split())
    # အကိုလေး အသံနှုန်းအတွက် ပျမ်းမျှ မြန်မာစာ ၁ လုံးလျှင် ၀.၁၈ စက္ကန့် တွက်ချက်သည်
    estimated_seconds = math.ceil(char_count * 0.18) 
    st.write(f"📝 စာလုံးရေ: {char_count} | စကားလုံး: {word_count} | ⏱️ ခန့်မှန်းကြာချိန်: {estimated_seconds} စက္ကန့်")

st.subheader("🤖 TTS Engine")
engine = st.radio("Engine ရွေးချယ်ပါ -", ["အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)", "Gemini API"])

# Voice Option
voice_id = "V1" # Default
if engine == "အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)":
    voice_select = st.selectbox("အသံရွေးချယ်ရန် (Voice)", ["အကိုလေး (ကျား) - V1", "အမလေး (မ) - V2"])
    voice_id = "V1" if "အကိုလေး" in voice_select else "V2"
else:
    gemini_key = st.text_input("Gemini API Key ထည့်ပါ", type="password", help="Gemini အသံသုံးရန် သင့်ကိုယ်ပိုင် API Key လိုအပ်ပါသည်။")

file_name = st.text_input("သိမ်းဆည်းမည့် ဖိုင်နာမည် (File Name)", value="Myanmar_TTS")

# SRT Generator Helper Function
def generate_srt_content(text, total_seconds):
    # စာပိုဒ်ကို ပုဒ်ဖြတ် (။) သို့မဟုတ် ကော်မာ (၊) ဖြင့် ခွဲထုတ်ခြင်း
    sentences = [s.strip() for s in text.replace("၊", "။").split("။") if s.strip()]
    if not sentences:
        sentences = [text]
        
    srt_content = ""
    duration_per_sentence = total_seconds / len(sentences)
    current_time = 0.0
    
    for i, sentence in enumerate(sentences):
        start = current_time
        end = current_time + duration_per_sentence
        
        def fmt(secs):
            h = int(secs // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            ms = int((secs % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            
        srt_content += f"{i+1}\n{fmt(start)} --> {fmt(end)}\n{sentence}။\n\n"
        current_time = end
    return srt_content

# Generate Process
if st.button("🚀 Generate Audio & SRT", use_container_width=True):
    if not user_text:
        st.warning("ကျေးဇူးပြု၍ စာသားတစ်ခုခု အရင်ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("အသံဖိုင်နှင့် စာတန်းထိုးများကို ဖန်တီးနေပါသည်..."):
            
            mp3_file = f"{file_name}.mp3"
            srt_file = f"{file_name}.srt"
            
            # --- အကိုလေး TTS API LOGIC ---
            if "အကိုလေး" in engine:
                # အကိုလေး အများပြည်သူသုံး API Endpoint သို့ ချိတ်ဆက်ခြင်း
                api_url = "https://api.kolaytts.xyz/v1/synthesize" # နမူနာ Endpoint ဖြစ်သည်
                payload = {"text": user_text, "voice": voice_id, "speed": 1.0}
                
                try:
                    response = requests.post(api_url, json=payload, timeout=30)
                    if response.status_code == 200:
                        # ရလာတဲ့ Audio binary ကို mp3 အဖြစ်သိမ်းမည်
                        with open(mp3_file, "wb") as f:
                            f.write(response.content)
                            
                        # SRT ဖိုင်ထုတ်ခြင်း
                        srt_data = generate_srt_content(user_text, estimated_seconds)
                        with open(srt_file, "w", encoding="utf-8") as f:
                            f.write(srt_data)
                            
                        # UI တွင် ပြသခြင်း
                        st.success("🎉 အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။")
                        st.audio(mp3_file)
                        
                        with open(mp3_file, "rb") as f:
                            st.download_button("📥 MP3 Download", f, file_name=mp3_file, mime="audio/mp3", use_container_width=True)
                        with open(srt_file, "rb") as f:
                            st.download_button("📥 SRT Download", f, file_name=srt_file, mime="text/plain", use_container_width=True)
                    else:
                        st.error("အကိုလေး API Server အလုပ်မလုပ်သေးပါ။ gTTS (Google) ကို အစားထိုးသုံးပေးပါ။")
                except Exception as e:
                    st.error(f"ချိတ်ဆက်မှု မအောင်မြင်ပါ- {e}")
            
            # --- GEMINI API LOGIC ---
            else:
                if not gemini_key:
                    st.error("Gemini API Key ထည့်သွင်းရန် လိုအပ်ပါသည်။")
                else:
                    # ဤနေရာတွင် Gemini API သို့ စာသားပို့ပြီး Audio ပြန်ယူသည့် စနစ်ကို ရေးရပါမည်
                    st.warning("Gemini TTS Engine ကို လောလောဆယ် စမ်းသပ်ဆဲ အဆင့်သာ ဖြစ်ပါသည်။")
                            
