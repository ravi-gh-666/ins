document.addEventListener('DOMContentLoaded', function() {
    function sanitize(str) {
        return str ? str.replace(/[^a-zA-Z0-9]/g, '') : '';
    }
    var container = document.querySelector('.container');
    var insurer = sanitize(container ? container.getAttribute('data-policy-insurer') : '');
    var policy = sanitize(container ? container.getAttribute('data-policy-name') : '');
    var langSel = document.getElementById('policy-doc-lang');
    var docLinks = {
        'prospectus-link': 'prospectus.pdf',
        'policywordings-link': 'policy_wordings.pdf',
        'brochure-link': 'brochure.pdf',
        'networklist-link': 'network_list.pdf'
    };
    function updateLinks() {
        var lang = langSel.value;
        Object.entries(docLinks).forEach(function([id, fname]) {
            var el = document.getElementById(id);
            if (el) {
                el.href = `/static/policy_docs/${insurer}/${policy}/${lang}/${fname}`;
            }
        });
    }
    if (langSel) {
        langSel.addEventListener('change', updateLinks);
        updateLinks();
    }
});
