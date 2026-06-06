import streamlit as st
import requests
import io
import math
from pydub import AudioSegment

st.set_page_config(page_title="Myanmar TTS & SRT", page_icon="🎙️")
st.title("🎙️ Myanmar TTS & SRT Generator")
st.info("👑 ကြော်ငြာပါ၊ အချိန်စောင့်စရာမလိုဘဲ အကန့်အသတ်မရှိ သုံးချင်ပါက VIP ဝယ်ယူရန် နှိပ်ပါ။")

user_text = st.text_area("မြန်မာစာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ -", height=200, placeholder="ဒီမှာ မြန်မာစာ ရိုက်ထည့်ပါ...")

# စာလုံးရေနှင့် အချိန် တွက်ချက်ခြင်း
if user_text:
    char_count = len(user_text)
    word_count = len(user_text.split())
    estimated_seconds = math.ceil(char_count * 0.20) 
    st.write(f"📝 စာလုံးရေ: {char_count} | စကားလုံး: {word_count} | ⏱️ ခန့်မှန်းကြာချိန်: {estimated_seconds} စက္ကန့်")

st.subheader("🤖 TTS Engine")
engine = st.radio("Engine ရွေးချယ်ပါ -", ["အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)", "Gemini API (VIP)"])

# အသံရွေးချယ်ရန် Dropdown
voice_select = st.selectbox(
    "🎙️ အသံရွေးချယ်ရန် (Voice)", 
    [
        "အကိုလေး (မြန်မာ - ယောက်ျားလေးသံစစ်စစ်)", 
        "အမလေး (မြန်မာ - မိန်းကလေးသံစစ်စစ်)"
    ]
)

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
        st.warning("ကျေးဇူးပြု၍ စာသားတစ်ခုခု အရင်ရိုက်ထည့်ပါ")
    else:
        with st.spinner("အသံဖိုင်နှင့် စာတန်းထိုးများကို ဖန်တီးနေပါသည်..."):
            try:
                # Google Translate Direct Audio API ကို အသုံးပြုခြင်း
                base_url = "https://translate.google.com/translate_tts"
                params = {
                    "ie": "UTF-8",
                    "q": user_text,
                    "tl": "my",
                    "client": "tw-ob",
                    "total": 1,
                    "idx": 0,
                    "textlen": len(user_text)
                }
                
                response = requests.get(base_url, params=params, timeout=20)
                
                if response.status_code == 200:
                    raw_audio = response.content
                    
                    # ယောက်ျားလေးသံ (အကိုလေး) ရွေးထားရင် အသံ Pitch ကို နိမ့်ချပြီး ယောက်ျားသံပြောင်းမည်
                    if "ယောက်ျားလေးသံ" in voice_select:
                        sound = AudioSegment.from_file(io.BytesIO(raw_audio), format="mp3")
                        
                        # Pitch ကို ယောက်ျားလေးအသံ Tone ထွက်အောင် အောက်သို့ နှိမ့်ချလိုက်ခြင်း
                        new_sample_rate = int(sound.frame_rate * 0.78)
                        male_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
                        male_sound = male_sound.set_frame_rate(sound.frame_rate)
                        
                        # အသံဖိုင်အဖြစ် ပြန်ပြောင်းခြင်း
                        buffer = io.BytesIO()
                        male_sound.export(buffer, format="mp3")
                        audio_bytes = buffer.getvalue()
                    else:
                        # မိန်းကလေးသံအတွက် Google ရဲ့ မူရင်းအသံအတိုင်း သုံးမည်
                        audio_bytes = raw_audio
                    
                    # SRT ဖိုင် တွက်ချက်ထုတ်ပေးခြင်း
                    srt_data = generate_srt_content(user_text, estimated_seconds)
                    
                    st.success("🎉 အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။")
                    
                    # UI တွင် ပြသခြင်း
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
                    st.error("Google Server ထံမှ အသံဒေတာ ဆွဲယူ၍မရပါ။")
                    
            except Exception as e:
                st.error(f"လုပ်ဆောင်မှု အမှန်တကယ် မအောင်မြင်ပါ- {e}")
    
