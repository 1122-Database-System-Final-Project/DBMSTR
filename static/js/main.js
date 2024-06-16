
// 註冊一個事件監聽器, 在整個 HTML 文件完全加載和解析完畢後執行
document.addEventListener('DOMContentLoaded', function() {
    popTimeOptions();
    setupEventListeners(); // 設置特別的事件監聽器函數來監控指定變數的變化
    initializeSeatSelection(); // 初始化座位選擇功能
});

// 顯示時間列表
function popTimeOptions() {
    const startTimeSelect = document.getElementById('start_time');
    const endTimeSelect = document.getElementById('end_time');
    const start = new Date();
    const end = new Date(start);
    end.setDate(start.getDate() + 7);

    let current = new Date(start);
    while (current <= end) {
        for (let h = 6; h < 24; h++) {
            for (let m = 0; m < 60; m += 30) {
                const time = current.toISOString().split('T')[0] + ` ${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
                startTimeSelect.add(new Option(time, time));
                endTimeSelect.add(new Option(time, time));
            }
        }
        current.setDate(current.getDate() + 1);
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

function showSeats(car_id) {
    // JavaScript 用於顯示特定車廂的座位
    let seatsDiv = document.getElementById('seats');
    // 根據 car_id 更新 seatsDiv 的內容
}

function cancelSelection() {
    window.location.href = "{{ url_for('query_train') }}";
}

function initializeSeatSelection() {
    const carButtons = document.querySelectorAll('button[onclick^="showSeats"]');
    carButtons.forEach(button => {
        button.addEventListener('click', function() {
            const carId = this.getAttribute('onclick').match(/\d+/)[0];
            showSeats(carId);
        });
    });

    const cancelSelectionButton = document.querySelector('button[onclick="cancelSelection()"]');
    if (cancelSelectionButton) {
        cancelSelectionButton.addEventListener('click', cancelSelection);
    }
}

function showSeats(carId) {
    // 在這裡更新座位顯示邏輯
    let seatsDiv = document.getElementById('seats');
    // 清空現有的座位顯示
    seatsDiv.innerHTML = '';
    // 假設我們從後端獲取的座位數據已經存儲在 window.seatsData 中
    window.seatsData.forEach(seat => {
        if (seat.car_id == carId) {
            let seatElement = document.createElement('label');
            seatElement.textContent = seat.seat_id;
            let checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.name = 'selected_seats';
            checkbox.value = `${seat.car_id}-${seat.seat_id}`;
            if (seat.is_available == 0) {
                checkbox.disabled = true;
            } else {
                checkbox.classList.add('highlight');
            }
            seatElement.appendChild(checkbox);
            seatsDiv.appendChild(seatElement);
        }
    });
}

function cancelSelection() {
    window.location.href = "/query_train";
}