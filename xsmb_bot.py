import asyncio
import random
from collections import Counter
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7618979983:AAGDWrAVf6NgNkBTa7dS-kmH0k5BbWHhNw8"
lottery_history = []
session_count = 0

def generate_random_lottery():
    """Tạo kết quả xổ số ngẫu nhiên."""
    result = {
        "Giải Đặc Biệt": str(random.randint(0, 99999)).zfill(5),
        "Giải Nhất": str(random.randint(0, 99999)).zfill(5),
        "Giải Nhì": [str(random.randint(0, 99999)).zfill(5) for _ in range(2)],
        "Giải Ba": [str(random.randint(0, 99999)).zfill(5) for _ in range(6)],
        "Giải Tư": [str(random.randint(0, 99999)).zfill(5) for _ in range(4)],
        "Giải Năm": [str(random.randint(0, 99999)).zfill(5) for _ in range(6)],
        "Giải Sáu": [str(random.randint(0, 999)).zfill(3) for _ in range(3)],
        "Giải Bảy": [str(random.randint(0, 99)).zfill(2) for _ in range(4)],
    }
    return result

async def send_lottery_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /quaythu."""
    global session_count
    session_count += 1
    user = update.effective_user
    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎲 {user.mention_html()} đang quay thử kết quả xổ số... Chúc Bạn May Mắn!",
        parse_mode="HTML"
    )
    await asyncio.sleep(5)  # Chờ 5 giây

    # Tạo kết quả xổ số
    result = generate_random_lottery()
    lottery_history.append(result)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    message = f"🎲 <b>KẾT QUẢ QUAY THỬ XỔ SỐ MIỀN BẮC</b> 🎲\n\n"
    message += f"🕒 <b>Ngày giờ:</b> {now}\n"
    message += f"🔢 <b>Phiên:</b> #{session_count}\n"
    message += f"👤 <b>Người quay:</b> {user.mention_html()}\n\n"

    for prize, numbers in result.items():
        if isinstance(numbers, list):
            numbers = " - ".join(numbers)
        message += f"<b>{prize}:</b> {numbers}\n"

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

async def guess_two_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /quaythux2 <số1><số2>. So sánh với 2 số cuối của tổng 8 giải."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    if len(context.args) != 1:
        await update.message.reply_text("Vui lòng nhập 4 số mà bạn muốn chọn (ví dụ: /quaythux2 3563).")
        return

    user_guess = context.args[0]

    if len(user_guess) != 4 or not user_guess.isdigit():
        await update.message.reply_text("Số bạn nhập không hợp lệ. Vui lòng nhập theo định dạng: <số1><số2> (ví dụ: 3563).")
        return

    # Lấy hai số đã chọn
    num1 = user_guess[:2]  # Hai ký tự đầu tiên
    num2 = user_guess[2:]  # Hai ký tự sau cùng

    # Quay thử xổ số
    await send_lottery_result(update, context)  # Gọi hàm quay thử để lấy kết quả
    result = lottery_history[-1]  # Lấy kết quả quay thử cuối cùng

    # Lấy 2 số cuối của tất cả các giải
    last_two_digits_list = [result[prize][-2:] for prize in result.keys()]

    # Kiểm tra các số người dùng đã chọn
    matched_numbers = [num for num in [num1, num2] if num in last_two_digits_list]

    if len(matched_numbers) == 2:
        await context.bot.send_message(chat_id=chat_id, text=f"🎉 Chúc mừng {user.mention_html()}! Bạn đã chọn đúng: {', '.join(matched_numbers)} 🎉", parse_mode="HTML")
    elif matched_numbers:
        # Thông báo cho người dùng nếu một số đã chọn xuất hiện
        missing_numbers = [num for num in [num1, num2] if num not in matched_numbers]
        counts = {num: last_two_digits_list.count(num) for num in matched_numbers}
        message = ", ".join(f"{num} ({counts[num]} nháy)" for num in matched_numbers)
        await context.bot.send_message(chat_id=chat_id, text=f"😢 Rất tiếc, {user.mention_html()}! Bạn đã chọn {message} nhưng thiếu {', '.join(missing_numbers)}. Chúc bạn may mắn lần sau!", parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"😢 Rất tiếc, {user.mention_html()}! Bạn đã không chọn đúng số nào trong kỳ quay thử. Chúc Bạn May Mắn lần Sau!", parse_mode="HTML")

async def guess_de(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /quaythude <số>. So sánh với 2 số cuối của Giải Đặc Biệt."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    if len(context.args) != 1:
        await update.message.reply_text("Vui lòng nhập một số mà bạn muốn chọn (ví dụ: /quaythude 25).")
        return

    user_guess = context.args[0]

    if len(user_guess) != 2 or not user_guess.isdigit():
        await update.message.reply_text("Số bạn nhập không hợp lệ. Vui lòng nhập theo định dạng: <số> (ví dụ: 25).")
        return

    await send_lottery_result(update, context)  # Gọi hàm quay thử để lấy kết quả
    result = lottery_history[-1]  # Lấy kết quả quay thử cuối cùng

    last_two_digits_de = result["Giải Đặc Biệt"][-2:]  # Hai số cuối của Giải Đặc Biệt

    if user_guess == last_two_digits_de:
        await context.bot.send_message(chat_id=chat_id, text=f"🎉 Chúc mừng {user.mention_html()}! Bạn đã chọn đúng Giải Đặc Biệt 🎉", parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"😢 Rất tiếc, {user.mention_html()}! Bạn đã không chọn đúng Giải Đặc Biệt. Thử lại nhé!", parse_mode="HTML")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /quaythu_xs để thống kê các số cuối của tất cả các phiên."""
    chat_id = update.effective_chat.id

    if not lottery_history:
        await context.bot.send_message(chat_id=chat_id, text="Chưa có kết quả nào để thống kê.")
        return

    last_two_digits = []

    # Lấy hai số cuối của tất cả các giải trong tất cả các phiên
    for result in lottery_history:
        for prize in result.values():
            if isinstance(prize, list):
                last_two_digits.extend([num[-2:] for num in prize])
            else:
                last_two_digits.append(prize[-2:])

    # Đếm tần suất của mỗi cặp số
    counter = Counter(last_two_digits)

    # Lấy 10 cặp số xuất hiện nhiều nhất và ít nhất
    most_common = counter.most_common(10)
    least_common = counter.most_common()[:-11:-1]

    total_count = sum(counter.values())
    message = "<b>THỐNG KÊ SỐ CUỐI CÙNG</b>\n\n"

    # Thống kê tần suất và tỷ lệ phần trăm cho các cặp số nhiều nhất
    message += "<b>10 CẶP SỐ NHIỀU NHẤT:</b>\n"
    for num, count in most_common:
        percentage = (count / total_count) * 100
        message += f"{num}: {count} lần ({percentage:.2f}%)\n"

    # Thống kê tần suất và tỷ lệ phần trăm cho các cặp số ít nhất
    message += "\n<b>10 CẶP SỐ ÍT NHẤT:</b>\n"
    for num, count in least_common:
        percentage = (count / total_count) * 100
        message += f"{num}: {count} lần ({percentage:.2f}%)\n"

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

def main():
    """Chạy bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("quaythu", send_lottery_result))
    application.add_handler(CommandHandler("quaythux2", guess_two_numbers))
    application.add_handler(CommandHandler("quaythude", guess_de))
    application.add_handler(CommandHandler("quaythu_xs", statistics))

    print("Bot đang khởi chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
