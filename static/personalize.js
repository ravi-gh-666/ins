document.addEventListener('DOMContentLoaded', function() {
    var catSel = document.getElementById('category');
    if (catSel) {
        catSel.addEventListener('change', function() {
            this.form.submit();
        });
    }
});