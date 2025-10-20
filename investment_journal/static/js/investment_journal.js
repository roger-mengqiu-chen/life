const lossColor = "rgba(252,3,3,0.43)"
const earningColor = "rgba(167,245,115,0.82)"

const render = () => {
    const rateCells = document.querySelectorAll(".field-earning_rate");
    rateCells.forEach(rateCell => {
        const value = parseFloat(rateCell.innerText);
        const row = rateCell.parentElement;
        if (value > 0) {
            row.style.background = earningColor;
        }
        else if (value < 0) {
            row.style.background = lossColor;
        }
    })
}

document.addEventListener("DOMContentLoaded", render);
