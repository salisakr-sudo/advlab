#!/usr/bin/env python3
"""
============================================================
ชื่อโปรแกรม : dlyoutube.py
วัตถุประสงค์ : โปรแกรมดาวน์โหลดวิดีโอจาก YouTube
ไลบรารีที่ใช้: yt-dlp (ติดตั้งด้วย pip install yt-dlp)
ผู้เขียน    : นักศึกษา advlab2
วันที่      : 2026
============================================================
"""

# นำเข้าไลบรารีที่จำเป็น
import yt_dlp          # ไลบรารีหลักสำหรับดาวน์โหลด YouTube
import os              # ใช้จัดการไฟล์และโฟลเดอร์
import sys             # ใช้รับ argument จาก command line


# ============================================================
# ฟังก์ชัน: show_menu()
# วัตถุประสงค์: แสดงเมนูตัวเลือกให้ผู้ใช้เลือกรูปแบบการดาวน์โหลด
# ============================================================
def show_menu():
    print("\n" + "=" * 50)
    print("   🎬  YouTube Downloader - advlab2")
    print("=" * 50)
    print("  [1] ดาวน์โหลดวิดีโอ (คุณภาพสูงสุด)")
    print("  [2] ดาวน์โหลดวิดีโอ (720p)")
    print("  [3] ดาวน์โหลดวิดีโอ (480p)")
    print("  [4] ดาวน์โหลดเฉพาะเสียง (MP3)")
    print("  [5] ดูรายการคุณภาพที่มีทั้งหมด")
    print("  [0] ออกจากโปรแกรม")
    print("=" * 50)


# ============================================================
# ฟังก์ชัน: get_video_info(url)
# วัตถุประสงค์: ดึงข้อมูลวิดีโอก่อนดาวน์โหลด (ชื่อ, ความยาว, ฯลฯ)
# พารามิเตอร์: url (str) - ลิงก์ YouTube
# คืนค่า    : dict ข้อมูลวิดีโอ หรือ None หากเกิดข้อผิดพลาด
# ============================================================
def get_video_info(url):
    # ตั้งค่า yt-dlp ให้แค่ดึงข้อมูล ไม่ดาวน์โหลดจริง
    ydl_opts = {
        'quiet': True,         # ปิดการแสดงข้อความ log
        'no_warnings': True,   # ปิด warning
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info() พร้อม download=False → ดึงข้อมูลอย่างเดียว
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        print(f"  ❌ ไม่สามารถดึงข้อมูลวิดีโอได้: {e}")
        return None


# ============================================================
# ฟังก์ชัน: list_formats(url)
# วัตถุประสงค์: แสดงรายการรูปแบบ/คุณภาพวิดีโอทั้งหมดที่มี
# พารามิเตอร์: url (str) - ลิงก์ YouTube
# ============================================================
def list_formats(url):
    print("\n  🔍 กำลังดึงรายการรูปแบบวิดีโอ...")

    info = get_video_info(url)
    if not info:
        return

    print(f"\n  📺 ชื่อวิดีโอ: {info.get('title', 'ไม่ทราบ')}")
    print(f"  ⏱  ความยาว  : {info.get('duration', 0) // 60} นาที {info.get('duration', 0) % 60} วินาที")
    print(f"\n  {'Format ID':<12} {'Extension':<10} {'Resolution':<15} {'Note'}")
    print("  " + "-" * 60)

    # วนลูปแสดงทุก format ที่ YouTube มีให้
    for fmt in info.get('formats', []):
        fmt_id     = fmt.get('format_id', '-')
        ext        = fmt.get('ext', '-')
        resolution = fmt.get('resolution', '-') or fmt.get('format_note', '-')
        note       = fmt.get('format_note', '')
        print(f"  {fmt_id:<12} {ext:<10} {resolution:<15} {note}")


# ============================================================
# ฟังก์ชัน: download_video(url, quality, output_path)
# วัตถุประสงค์: ดาวน์โหลดวิดีโอตามคุณภาพที่กำหนด
# พารามิเตอร์:
#   url         (str) - ลิงก์ YouTube
#   quality     (str) - รหัสคุณภาพ เช่น 'best', '720', '480'
#   output_path (str) - โฟลเดอร์ที่จะบันทึกไฟล์
# ============================================================
def download_video(url, quality='best', output_path='downloads'):
    # สร้างโฟลเดอร์ปลายทางถ้ายังไม่มี
    os.makedirs(output_path, exist_ok=True)

    # กำหนด format string ตามคุณภาพที่เลือก
    if quality == 'best':
        # bestvideo + bestaudio → รวมเป็นไฟล์เดียวด้วย ffmpeg
        fmt = 'bestvideo+bestaudio/best'
    elif quality in ('720', '480', '360'):
        # เลือกวิดีโอที่ความสูงไม่เกินที่กำหนด + เสียงที่ดีที่สุด
        fmt = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
    else:
        fmt = 'best'  # fallback กรณีไม่รู้จัก quality

    # ตั้งค่าตัวเลือกสำหรับ yt-dlp
    ydl_opts = {
        'format': fmt,
        # รูปแบบชื่อไฟล์: ชื่อวิดีโอ.นามสกุล (ตัดอักขระพิเศษออก)
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        # รวมวิดีโอและเสียงให้เป็นไฟล์ MP4 เดียว (ต้องติดตั้ง ffmpeg)
        'merge_output_format': 'mp4',
        # แสดงแถบความคืบหน้าระหว่างดาวน์โหลด
        'progress_hooks': [progress_hook],
    }

    print(f"\n  📥 เริ่มดาวน์โหลด (คุณภาพ: {quality}p หรือสูงสุด)...")
    print(f"  📁 บันทึกไปที่: {os.path.abspath(output_path)}\n")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])   # เริ่มดาวน์โหลดจริง
        print("\n  ✅ ดาวน์โหลดสำเร็จ!")
    except yt_dlp.utils.DownloadError as e:
        print(f"\n  ❌ ดาวน์โหลดไม่สำเร็จ: {e}")
    except Exception as e:
        print(f"\n  ❌ เกิดข้อผิดพลาด: {e}")


# ============================================================
# ฟังก์ชัน: download_audio(url, output_path)
# วัตถุประสงค์: ดาวน์โหลดและแปลงเสียงเป็นไฟล์ MP3
# พารามิเตอร์:
#   url         (str) - ลิงก์ YouTube
#   output_path (str) - โฟลเดอร์ที่จะบันทึกไฟล์
# ============================================================
def download_audio(url, output_path='downloads'):
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',   # เลือกเสียงคุณภาพสูงสุด
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        # postprocessors: แปลงไฟล์เสียงเป็น MP3 หลังดาวน์โหลด
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',   # ใช้ ffmpeg แยกเสียง
            'preferredcodec': 'mp3',       # แปลงเป็น mp3
            'preferredquality': '192',     # bitrate 192 kbps
        }],
        'progress_hooks': [progress_hook],
    }

    print(f"\n  🎵 กำลังดาวน์โหลดและแปลงเป็น MP3...")
    print(f"  📁 บันทึกไปที่: {os.path.abspath(output_path)}\n")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n  ✅ ดาวน์โหลด MP3 สำเร็จ!")
    except Exception as e:
        print(f"\n  ❌ เกิดข้อผิดพลาด: {e}")


# ============================================================
# ฟังก์ชัน: progress_hook(d)
# วัตถุประสงค์: callback function แสดงความคืบหน้าการดาวน์โหลด
# พารามิเตอร์: d (dict) - ข้อมูลสถานะจาก yt-dlp
# ============================================================
def progress_hook(d):
    if d['status'] == 'downloading':
        # ดึง % ความคืบหน้า (ลบ ANSI color codes ออก)
        percent = d.get('_percent_str', '?%').strip()
        speed   = d.get('_speed_str', '?').strip()
        eta     = d.get('_eta_str', '?').strip()
        # \r → เขียนทับบรรทัดเดิม (แสดงความคืบหน้าแบบ inline)
        print(f"\r  ⬇️  {percent} | ความเร็ว: {speed} | เหลืออีก: {eta}   ", end='')

    elif d['status'] == 'finished':
        print(f"\n  ✔️  ดาวน์โหลดเสร็จ กำลังประมวลผลไฟล์...")


# ============================================================
# ฟังก์ชัน: main()
# วัตถุประสงค์: จุดเริ่มต้นโปรแกรม ควบคุมการทำงานหลัก
# ============================================================
def main():
    print("\n" + "=" * 50)
    print("  ยินดีต้อนรับสู่ YouTube Downloader")
    print("  สร้างโดย: advlab2")
    print("=" * 50)

    # รับ URL จากผู้ใช้
    url = input("\n  กรุณาป้อน YouTube URL: ").strip()

    # ตรวจสอบว่า URL ไม่ว่างเปล่า
    if not url:
        print("  ❌ กรุณาป้อน URL ก่อน")
        return

    # แสดงข้อมูลวิดีโอก่อนดาวน์โหลด
    print("\n  🔍 กำลังดึงข้อมูลวิดีโอ...")
    info = get_video_info(url)
    if info:
        print(f"  📺 ชื่อ    : {info.get('title', 'ไม่ทราบ')}")
        print(f"  👤 ช่อง   : {info.get('uploader', 'ไม่ทราบ')}")
        duration = info.get('duration', 0)
        print(f"  ⏱  ความยาว: {duration // 60} นาที {duration % 60} วินาที")
    else:
        print("  ⚠️  ไม่สามารถดึงข้อมูลได้ แต่จะลองดาวน์โหลดต่อไป")

    # วนลูปแสดงเมนูจนกว่าผู้ใช้จะเลือก 0
    while True:
        show_menu()
        choice = input("  เลือกรายการ (0-5): ").strip()

        if choice == '1':
            download_video(url, quality='best')
            break

        elif choice == '2':
            download_video(url, quality='720')
            break

        elif choice == '3':
            download_video(url, quality='480')
            break

        elif choice == '4':
            download_audio(url)
            break

        elif choice == '5':
            list_formats(url)
            # หลังดูรายการแล้ว ให้เลือกใหม่

        elif choice == '0':
            print("\n  👋 ออกจากโปรแกรม ขอบคุณที่ใช้งาน")
            sys.exit(0)

        else:
            print("  ⚠️  กรุณาเลือก 0-5 เท่านั้น")


# ============================================================
# จุดเริ่มต้นโปรแกรม
# __name__ == '__main__' → รันตรงๆ ไม่ใช่ import เป็น module
# ============================================================
if __name__ == '__main__':
    main()
