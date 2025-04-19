document.addEventListener("DOMContentLoaded", function () {
        let counters = document.querySelectorAll(".card h1");
        counters.forEach(counter => {
            let target = +counter.innerText;
            let count = 0;
            let increment = target / 100;
            let interval = setInterval(() => {
                count += increment;
                if (count >= target) {
                    count = target;
                    clearInterval(interval);
                }
                counter.innerText = Math.floor(count);
            }, 20);
        });
    });