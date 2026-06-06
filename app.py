import streamlit as st
import requests
import math

st.set_page_config(page_title="Myanmar TTS & SRT", page_icon="🎙️")
st.title("🎙️ Myanmar TTS & SRT Generator")
st.info("👑 ကြော်ငြာပါ၊ အချိန်စောင့်စရာမလိုဘဲ အကန့်အသတ်မရှိ သုံးချင်ပါက VIP ဝယ်ယူရန် နှိပ်ပါ။")

user_text = st.text_area("မြန်မာစာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ -", height=200, placeholder="ဒီမှာ မြန်မာစာ ရိုက်ထည့်ပါ...")

# စာလုံးရေနှင့် အချိန် တွက်ချက်ခြင်း
if user_text:
    char_count = len(user_text)
    word_count = len(user_text.split())
    estimated_seconds = math.ceil(char_count * 0.18) 
    st.write(f"📝 စာလုံးရေ: {char_count} | စကားလုံး: {word_count} | ⏱️ ခန့်မှန်းကြာချိန်: {estimated_seconds} စက္ကန့်")

st.subheader("🤖 TTS Engine")
engine = st.radio("Engine ရွေးချယ်ပါ -", ["အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)", "Gemini API (VIP)"])

# တကယ့် အကိုလေး ရဲ့ Voice IDs များ
voice_id = "male_01" # Default

if engine == "အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)":
    voice_select = st.selectbox(
        "🎙️ အသံရွေးချယ်ရန် (Voice)", 
        [
            "အကိုလေး (မြန်မာ - ယောက်ျားလေးသံစစ်စစ်)", 
            "အမလေး (မြန်မာ - မိန်းကလေးသံစစ်စစ်)"
        ]
    )
    
    if "ယောက်ျားလေးသံ" in voice_select:
        voice_id = "male_01"      # အကိုလေး အသံစစ်စစ်
    else:
        voice_id = "female_01"    # အမလေး အသံစစ်စစ်
else:
    st.warning("Gemini API Engine ကို အသုံးပြုရန် သီးသန့် VIP Setup လိုအပ်ပါသည်။")

file_name = st.text_input("သိမ်းဆည်းမည့် ဖိုင်နာမည် (File Name)", value="Myanmar_TTS")

# SRT (စာတန်းထိုး) ဖန်တီးပေးမည့် Engine
def generate_srt_content(text, total_seconds):
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

# Button Click Trigger
if st.button("🚀 Generate Audio & SRT", use_container_width=True):
    if not user_text:
        st.warning("ကျေးဇူးပြု၍ စာသားတစ်ခုခု အရင်ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("အသံဖိုင်နှင့် စာတန်းထိုးများကို ဖန်တီးနေပါသည်..."):
            try:
                # မူရင်း ဝဘ်ဆိုဒ်က သုံးထားတဲ့ တကယ့် API Endpoint အစစ်အမှန်
                api_url = "https://api.kolaytts.xyz/api/v1/tts" 
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": user_text,
                    "voice_id": voice_id,
                    "speed": 1.0
                }
                
                # API ဆီ လှမ်းတောင်းခြင်း
                response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    
                    # SRT ဖိုင် တွက်ချက်ထုတ်ပေးခြင်း
                    srt_data = generate_srt_content(user_text, estimated_seconds)
                    
                    st.success("🎉 အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။")
                    
                    # UI တွင် အသံနှင့် ဒေါင်းလုဒ်ခလုတ်များ ပြသခြင်း
                    st.subheader("🎵 Output Audio")
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    st.subheader("💾 ဒေါင်းလုဒ်ရယူရန်")
                    
                    st.download_button(
                        label="📥 MP3 Download", 
                        data=audio_bytes, 
                        file_name=f"{file_name}.mp3", 
                        mime="audio/mp3", 
                        use_container_width=True
                    )
                    
                    st.download_button(
                        label="📥 SRT Download", 
                        data=srt_data.encode('utf-8'), 
                        file_name=f"{file_name}.srt", 
                        mime="text/plain", 
                        use_container_width=True
                    )
                else:
                    st.error(f"API မှ တုံ့ပြန်မှု မရှိပါ။ (Status Code: {response.status_code})")
                    
            except Exception as e:
                st.error(f"လုပ်ဆောင်မှု မအောင်မြင်ပါ (Server Error)- {e}")

