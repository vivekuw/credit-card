//function parseCustomDate(dateString) {
//    let months = {
//        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
//        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
//        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
//    };
//
//    let parts = dateString.split(" ");
//    if (parts.length < 3) return ""; // Handle invalid dates
//
//    let month = months[parts[0]]; // Convert "Oct" → "10"
//    let day = parts[1].replace(",", "").padStart(2, "0"); // Ensure two-digit day
//    let year = parts[2];
//
//    return `${year}-${month}-${day}`; // Convert to YYYY-MM-DD
//}  // **← Missing closing bracket added here**

document.addEventListener("DOMContentLoaded", function () {
    let dateFilter = document.getElementById("dateFilter");
    let table = document.getElementById("fraudtable");

    if (!dateFilter || !table) {
        console.error("Element with ID 'dateFilter' or 'fraudtable' not found!");
        return;
    }

    dateFilter.addEventListener("change", function () {
        let selectedDate = dateFilter.value; // YYYY-MM-DD format
        console.log("Selected Date:", selectedDate);

        let rows = table.getElementsByTagName("tr");

        for (let i = 1; i < rows.length; i++) {
            let dateCell = rows[i].getElementsByTagName("td")[4]; // 5th column (0-based index)
            if (!dateCell) continue;

            let rowDate = dateCell.textContent.trim(); // Format: "Feb 26, 2025"
            let formattedRowDate = convertToYYYYMMDD(rowDate);

            console.log("Row Date:", rowDate, "->", formattedRowDate);

            // Show/hide row based on comparison
            rows[i].style.display = (selectedDate === "" || formattedRowDate === selectedDate) ? "" : "none";
        }
    });

    function convertToYYYYMMDD(dateString) {
        let months = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        };

        let parts = dateString.split(" ");
        if (parts.length < 3) return ""; // Handle invalid date format

        let month = months[parts[0]]; // Convert "Feb" → "02"
        let day = parts[1].replace(",", "").padStart(2, "0"); // Ensure two-digit day
        let year = parts[2];

        return `${year}-${month}-${day}`; // Convert to YYYY-MM-DD
    }
});
