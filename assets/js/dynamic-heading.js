function updateHeading() {
    const now = new Date();
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    const weekday = weekdays[now.getDay()];
    
    // 获取当前时间
    const hours = now.getHours();
    let greeting;
    if (hours < 6) {
        greeting = '夜深了';
    } else if (hours < 9) {
        greeting = '早上好';
    } else if (hours < 12) {
        greeting = '上午好';
    } else if (hours < 14) {
        greeting = '中午好';
    } else if (hours < 17) {
        greeting = '下午好';
    } else if (hours < 19) {
        greeting = '傍晚好';
    } else {
        greeting = '晚上好';
    }

    // 格式化日期
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    
    // 更新标题
    const heading = document.querySelector('.banner-heading.home-heading');
    if (heading) {
        heading.innerHTML = `${greeting}，今天是${year}年${month}月${day}日 ${weekday}`;
    }
}

// 页面加载时更新一次
document.addEventListener('DOMContentLoaded', updateHeading);

// 每分钟更新一次
setInterval(updateHeading, 60000); 