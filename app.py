import streamlit as st
import asyncio
import edge_tts
import math

st.set_page_config(page_title="Myanmar TTS & SRT", page_icon="🎙️")
st.title("🎙️ Myanmar TTS & SRT Generator")
st.info("👑 ကြော်ငြာပါ၊ အချိန်စောင့်စရာမလိုဘဲ အကန့်အသတ်မရှိ သုံးချင်ပါက VIP ဝယ်ယူရန် နှိပ်ပါ။")

user_text = st.text_area("မြန်မာစာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ -", height=200, placeholder="ဒီမှာ မြန်မာစာ ရိုက်ထည့်ပါ...")

# စာလုံးရေနှင့် အချိန် တွက်ချက်ခြင်း
if user_text:
    char_count = len(user_text)
    word_count = len(user_text.split())
    estimated_seconds = math.ceil(char_count * 0.22) 
    st.write(f"📝 စာလုံးရေ: {char_count} | စကားလုံး: {word_count} | ⏱️ ခန့်မှန်းကြာချိန်: {estimated_seconds} စက္ကန့်")

st.subheader("🤖 TTS Engine")
engine = st.radio("Engine ရွေးချယ်ပါ -", ["အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)", "Gemini API (VIP)"])

# တကယ့် Microsoft Edge ရဲ့ သဘာဝကျတဲ့ မြန်မာ Voice IDs များ
voice_id = "my-MM-ZawZawNeural" # Default ကျားသံ

if engine == "အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)":
    voice_select = st.selectbox(
        "🎙️ အသံရွေးချယ်ရန် (Voice)", 
        [
            "အကိုလေး (မြန်မာ - ကျားသံ標準)", 
            "အမလေး (မြန်မာ - မိန်းကလေးသံ)"
        ]
    )
    
    if "ကျားသံ" in voice_select:
        voice_id = "my-MM-ZawZawNeural"      # တကယ့် ယောက်ျားလေးအသံစစ်စစ်
    else:
        voice_id = "my-MM-KhingNeural"        # တကယ့် မိန်းကလေးအသံစစ်စစ်
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

# Server ပိတ်ဆို့မှုမရှိအောင် ပိုမိုခိုင်မာစွာ ရေးသားထားသော Async Audio Downloader
async def make_voice(text, voice) -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# Button Click Trigger
if st.button("🚀 Generate Audio & SRT", use_container_width=True):
    if not user_text:
        st.warning("ကျေးဇူးပြု၍ စာသားတစ်ခုခု အရင်ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("အသံဖိုင်နှင့် စာတန်းထိုးများကို ဖန်တီးနေပါသည်..."):
            try:
                # Streamlit Server ပေါ်တွင် Event Loop ကို ပတ်ပတ်စက်စက် အသစ်ဆောက်ပြီး Run ခြင်း
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio_bytes = loop.run_until_complete(make_voice(user_text, voice_id))
                loop.close() # Connection ကို ပြန်ပိတ်ပေးသဖြင့် Error ကင်းစင်စေသည်
                
                if not audio_bytes or len(audio_bytes) < 100:
                    st.error("အသံဒေတာ ရယူ၍မရပါ။ စာသားကို တိုတိုဖြင့် ပြန်စမ်းကြည့်ပေးပါ။")
                else:
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
                    
            except Exception as e:
                st.error(f"လုပ်ဆောင်မှု မအောင်မြင်ပါ (Server Error)- {e}")
                
