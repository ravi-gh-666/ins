document.addEventListener('DOMContentLoaded', function() {
    var catSel = document.getElementById('category');
    if (catSel) {
        catSel.addEventListener('change', function() {
            this.form.submit();
        });
    }
    // Focus and scroll to plans table if present
    var plansTable = document.getElementById('plans-table');
    if (plansTable) {
        plansTable.scrollIntoView({ behavior: 'smooth', block: 'start' });
        plansTable.focus();
    }
});