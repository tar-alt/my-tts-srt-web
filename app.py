import streamlit as st
import asyncio
import edge_tts
import math
import os

st.set_page_config(page_title="Myanmar TTS & SRT", page_icon="🎙️")
st.title("🎙️ Myanmar TTS & SRT Generator")
st.info("👑 ကြော်ငြာပါ၊ အချိန်စောင့်စရာမလိုဘဲ အကန့်အသတ်မရှိ သုံးချင်ပါက VIP ဝယ်ယူရန် နှိပ်ပါ။")

user_text = st.text_area("မြန်မာစာသားများကို ဤနေရာတွင် ရိုက်ထည့်ပါ -", height=200, placeholder="ဒီမှာ မြန်မာစာ ရိုက်ထည့်ပါ...")

# စာလုံးရေနှင့် အချိန် တွက်ချက်ခြင်း
if user_text:
    char_count = len(user_text)
    word_count = len(user_text.split())
    # Edge TTS အတွက် ပျမ်းမျှ မြန်မာစာ ၁ လုံးလျှင် ၀.၁၈ စက္ကန့် ခန့်မှန်းတွက်ချက်သည်
    estimated_seconds = math.ceil(char_count * 0.18) 
    st.write(f"📝 စာလုံးရေ: {char_count} | စကားလုံး: {word_count} | ⏱️ ခန့်မှန်းကြာချိန်: {estimated_seconds} စက္ကန့်")

st.subheader("🤖 TTS Engine")
engine = st.radio("Engine ရွေးချယ်ပါ -", ["အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)", "Gemini API"])

# Voice Voice Selection
if engine == "အကိုလေးမြန်မာအသံအုပ်စု (ကျား/မ)":
    voice_select = st.selectbox("အသံရွေးချယ်ရန် (Voice)", ["အကိုလေး (ကျား) - ZawZaw", "အမလေး (မ) - Khing"])
    # Microsoft Edge ရဲ့ တရားဝင် မြန်မာ Voice ID များ
    voice_id = "my-MM-ZawZawNeural" if "အကိုလေး" in voice_select else "my-MM-KhingNeural"
else:
    st.warning("Gemini API Engine ကို အသုံးပြုရန် သီးသန့် Setup လိုအပ်ပါသည်။")
    voice_id = "my-MM-ZawZawNeural"

file_name = st.text_input("သိမ်းဆည်းမည့် ဖိုင်နာမည် (File Name)", value="Myanmar_TTS")

# SRT Generator Helper
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

# Async function for Edge TTS
async def amain(text, voice, mp3_path) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(mp3_path)

# Button Click Trigger
if st.button("🚀 Generate Audio & SRT", use_container_width=True):
    if not user_text:
        st.warning("ကျေးဇူးပြု၍ စာသားတစ်ခုခု အရင်ရိုက်ထည့်ပါ။")
    else:
        with st.spinner("အသံဖိုင်နှင့် စာတန်းထိုးများကို ဖန်တီးနေပါသည်..."):
            mp3_file = f"{file_name}.mp3"
            srt_file = f"{file_name}.srt"
            
            try:
                # Edge TTS ကို Run ပြီး MP3 သိမ်းခြင်း
                asyncio.run(amain(user_text, voice_id, mp3_file))
                
                # SRT ဖိုင် တွက်ချက်ထုတ်ပေးခြင်း
                srt_data = generate_srt_content(user_text, estimated_seconds)
                with open(srt_file, "w", encoding="utf-8") as f:
                    f.write(srt_data)
                
                # အောင်မြင်ကြောင်း UI ပြသခြင်း
                st.success("🎉 အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ။")
                
                st.subheader("🎵 Output Audio")
                st.audio(mp3_file)
                
                st.subheader("💾 ဒေါင်းလုဒ်ရယူရန်")
                with open(mp3_file, "rb") as f:
                    st.download_button("📥 MP3 Download", f, file_name=mp3_file, mime="audio/mp3", use_container_width=True)
                with open(srt_file, "rb") as f:
                    st.download_button("📥 SRT Download", f, file_name=srt_file, mime="text/plain", use_container_width=True)
                    
            except Exception as e:
                st.error(f"လုပ်ဆောင်မှု မအောင်မြင်ပါ- {e}")

