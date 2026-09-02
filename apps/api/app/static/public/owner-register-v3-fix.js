(function () {
    "use strict";
    let currentPane = 1;

    function showMessage(text, ok) {
        const box = document.getElementById("msg");
        if (!box) return;
        box.textContent = text;
        box.className = ok ? "msg ok" : "msg error";
    }

    function showPane(number) {
        if (number < 1 || number > 7) return;
        document.querySelectorAll(".pane").forEach(function (item) {
            item.classList.toggle("active", Number(item.dataset.pane) === number);
        });
        document.querySelectorAll(".steps .step").forEach(function (step, index) {
            step.classList.toggle("active", index + 1 === number);
            step.classList.toggle("done", index + 1 < number);
        });
        currentPane = number;
        window.scrollTo({ top: 0, behavior: "smooth" });
        if (number === 7 && typeof window.buildReview === "function") window.buildReview();
    }

    function validateRequired(pane) {
        for (const field of pane.querySelectorAll("input[required], select[required], textarea[required]")) {
            if (field.type === "checkbox") {
                if (!field.checked) { showMessage("Please complete the required confirmation.", false); field.focus(); return false; }
                continue;
            }
            if (!String(field.value || "").trim()) {
                const label = field.closest(".field")?.querySelector("label")?.textContent || "Required field";
                showMessage(label.replace("*", "").trim() + " is required.", false);
                field.focus(); return false;
            }
            if (!field.checkValidity()) { showMessage(field.validationMessage, false); field.focus(); return false; }
        }
        return true;
    }

    function validatePane() {
        const pane = document.querySelector('.pane[data-pane="' + currentPane + '"]');
        if (!pane || !validateRequired(pane)) return false;

        if (currentPane === 1) {
            const p = document.getElementById("owner_password");
            const c = document.getElementById("owner_password2");
            if (p && c && p.value !== c.value) { showMessage("Password and Confirm Password do not match.", false); c.focus(); return false; }
        }

        if (currentPane === 3) {
            const selected = document.querySelectorAll(".facility:checked").length;
            const extra = String(document.getElementById("additional_facilities")?.value || "").trim();
            if (!selected && !extra) { showMessage("Select at least one property facility.", false); return false; }
        }

        if (currentPane === 4) {
            const files = document.getElementById("hotel_files")?.files;
            if (!files || !files.length) { showMessage("Upload at least one hotel photo.", false); return false; }
        }

        if (currentPane === 5) {
            const cards = document.querySelectorAll("#rooms .repeat");
            if (!cards.length) { showMessage("Add at least one room category.", false); return false; }
            for (const card of cards) {
                const name = card.querySelector(".r-name")?.value.trim();
                const facilities = card.querySelectorAll(".rf:checked").length;
                const photos = card.querySelector(".r-files")?.files?.length || 0;
                if (!name) { showMessage("Every room category needs a room name.", false); card.querySelector(".r-name")?.focus(); return false; }
                if (!facilities) { showMessage("Room " + name + " needs at least one facility.", false); return false; }
                if (!photos) { showMessage("Room " + name + " needs at least one photo.", false); return false; }
            }
        }

        if (currentPane === 6) {
            const docs = document.querySelectorAll("#documents .repeat");
            if (!docs.length) { showMessage("Add at least one verification document.", false); return false; }
            for (const doc of docs) {
                if (!(doc.querySelector(".d-file")?.files?.length)) { showMessage("Please attach a file to every verification document.", false); return false; }
            }
        }
        return true;
    }

    // IMPORTANT: the HTML buttons already call nextPane()/prevPane().
    // The old fix also installed a click listener, so one click executed twice.
    // This controller is the single navigation path.
    window.nextPane = function () { if (validatePane() && currentPane < 7) showPane(currentPane + 1); };
    window.prevPane = function () { if (currentPane > 1) showPane(currentPane - 1); };
    window.previousPane = window.prevPane;
    window.goToPane = function (number) { showPane(Number(number)); };

    showPane(1);
})();
