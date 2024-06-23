
// 註冊一個事件監聽器, 在整個 HTML 文件完全加載和解析完畢後執行
document.addEventListener('DOMContentLoaded', function() {
    generateDateOptions(document.getElementById('travel_date'));
    generateTimeOptions(document.getElementById('start_time'));
    generateTimeOptions(document.getElementById('end_time'));
    setupEventListeners(); // 設置特別的事件監聽器函數來監控指定變數的變化
    // initializeSeatSelection(); // 初始化座位選擇功能
    initTicketTypeChangeEvent();
});

// 生成訂票日期選項
function generateDateOptions(selectElement) {
    const today = new Date();
    for (let i = 0; i < 7; i++) {
        let date = new Date();
        date.setDate(today.getDate() + i);
        let dateStr = date.toISOString().split('T')[0];
        let optionElement = document.createElement('option');
        optionElement.value = dateStr;
        optionElement.textContent = dateStr;
        selectElement.appendChild(optionElement);
    }
}

// 生成時間選項
function generateTimeOptions(selectElement) {
    const startHour = 6; // 開始時間: 6 AM
    const endHour = 24; // 結束時間: 12 AM
    const stepMinutes = 30; // 每30分鐘一個選項

    for (let hour = startHour; hour < endHour; hour++) {
        for (let minute = 0; minute < 60; minute += stepMinutes) {
            let hourStr = hour.toString().padStart(2, '0');
            let minuteStr = minute.toString().padStart(2, '0');
            let timeOption = `${hourStr}:${minuteStr}`;
            let optionElement = document.createElement('option');
            optionElement.value = timeOption;
            optionElement.textContent = timeOption;
            selectElement.appendChild(optionElement);
        }
    }
}

// 設置事件監聽器
function setupEventListeners() {
    document.getElementById('start_time').addEventListener('change', validateTimeSelection);
    document.getElementById('end_time').addEventListener('change', validateTimeSelection);
    document.getElementById('departure').addEventListener('input', validateStationSelection);
    document.getElementById('destination').addEventListener('input', validateStationSelection);
}

// 驗證時間選擇, 開始時間和結束時間不能相同
function validateTimeSelection() {
    const startTime = document.getElementById('start_time').value;
    const endTime = document.getElementById('end_time').value;
    const startTimeError = document.getElementById('start_time_error');
    const endTimeError = document.getElementById('end_time_error');

    if (startTime && endTime && startTime === endTime) {
        startTimeError.textContent = '開始時間和結束時間不能相同';
        endTimeError.textContent = '開始時間和結束時間不能相同';
    } else {
        startTimeError.textContent = '';
        endTimeError.textContent = '';
    }
}

// 驗證車站選擇, 出發車站和抵達車站不能相同
function validateStationSelection() {
    const departure = document.getElementById('departure').value;
    const destination = document.getElementById('destination').value;
    const departureError = document.getElementById('departure_error');
    const destinationError = document.getElementById('destination_error');

    if (departure && destination && departure === destination) {
        departureError.textContent = '出發車站和抵達車站不能相同';
        destinationError.textContent = '出發車站和抵達車站不能相同';
    } else {
        departureError.textContent = '';
        destinationError.textContent = '';
    }
}

// // 綁定所有票種選擇下拉菜單的變更事件到 handleTicketTypeChange
// function initTicketTypeChangeEvent() {
//     const ticketTypes = document.querySelectorAll('.ticket_type');
//     ticketTypes.forEach(ticketType => {
//         ticketType.addEventListener('change', handleTicketTypeChange);
//     });
// }

// // 處理票種變更事件, 呼叫 fetchTicketPrice 來獲取新的票價，並在成功獲取後更新對應的票價元素和總價
// function handleTicketTypeChange(event) {
//     const seatId = event.target.dataset.seatId;
//     const ticketTypeValue = event.target.value;
//     const priceElement = document.querySelector(`.ticket_price[data-seat-id="${seatId}"]`);

//     fetchTicketPrice(ticketTypeValue)
//         .then(price => {
//             updatePriceElement(priceElement, price);
//             updateTotalPrice();
//         })
//         .catch(error => console.error('Error fetching ticket price:', error));
// }

// // 發送請求到後端 API /calculate_ticket_price 來獲取票價，返回一個 Promise。
// function fetchTicketPrice(ticketType) {
//     return fetch(`/calculate_ticket_price?ticket_type=${ticketType}`)
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             return response.json();
//         })
//         .then(data => data.price)
//         .catch(error => {
//             console.error('Error fetching ticket price:', error);
//             return 0;  // 返回 0 確保價格更新
//         });
// }

// // 更新指定元素的票價
// function updatePriceElement(priceElement, price) {
//     priceElement.textContent = `${price} 元`;
// }

// // 計算並更新所有票價的總價
// function updateTotalPrice() {
//     const totalPriceElement = document.getElementById('total_price');
//     const prices = document.querySelectorAll('.ticket_price');
//     let totalPrice = 0;

//     prices.forEach(priceElement => {
//         const price = parseInt(priceElement.textContent.split(' ')[0], 10);
//         totalPrice += price;
//     });

//     totalPriceElement.textContent = totalPrice;
// }


function cancelSelection() {
    window.location.href = "/query_train";
}