function loadPolicies(insurerSelectId, policySelectId, selectedPolicyId) {
    const insurerId = document.getElementById(insurerSelectId).value;
    console.log('Loading policies for', insurerSelectId, 'with insurerId', insurerId, 'and selectedPolicyId', selectedPolicyId);
    fetch(`/api/policies/${insurerId}`)
        .then(response => response.json())
        .then(policies => {
            const policySelect = document.getElementById(policySelectId);
            policySelect.innerHTML = "";
            let found = false;
            policies.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.id;
                opt.textContent = p.name;
                if (selectedPolicyId && String(selectedPolicyId) === String(p.id)) {
                    opt.selected = true;
                    found = true;
                }
                policySelect.appendChild(opt);
            });
            if (!found && policies.length > 0) {
                policySelect.selectedIndex = 0;
                console.log('No selectedPolicyId matched, defaulting to first policy:', policies[0].id);
            }
            if (policies.length === 0) {
                console.log('No policies found for insurer', insurerId);
            }
        })
        .catch(err => {
            console.error('Error loading policies for', insurerId, err);
        });
}
window.addEventListener("DOMContentLoaded", function() {
    function getSelectedPolicyId(policySelectId) {
        var el = document.getElementById(policySelectId);
        var val = el.getAttribute('data-selected');
        console.log('Initial data-selected for', policySelectId, ':', val);
        return val;
    }
    loadPolicies("insurer1", "policy1", getSelectedPolicyId("policy1"));
    loadPolicies("insurer2", "policy2", getSelectedPolicyId("policy2"));
    document.getElementById("insurer1").addEventListener("change", function() {
        console.log('insurer1 changed to', this.value);
        loadPolicies("insurer1", "policy1", null);
    });
    document.getElementById("insurer2").addEventListener("change", function() {
        console.log('insurer2 changed to', this.value);
        loadPolicies("insurer2", "policy2", null);
    });
    // Focus to compare section if present
    setTimeout(function() {
        var summary = document.getElementById('compare-summary');
        var table = document.getElementById('compare-result');
        var anchor = document.getElementById('compare-anchor');
        if (summary) {
            summary.scrollIntoView({ behavior: 'smooth', block: 'start' });
            if (summary.focus) summary.focus();
        } else if (table) {
            table.scrollIntoView({ behavior: 'smooth', block: 'start' });
            if (table.focus) table.focus();
        } else if (anchor) {
            anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 200);
    document.querySelectorAll('.popular-compare-form').forEach(function(form) {
        form.addEventListener('click', function(e) {
            e.preventDefault();
            form.submit();
        });
        form.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                form.submit();
            }
        });
    });
    // Feature details dropdown toggle
    document.querySelectorAll('.feature-row').forEach(function(row) {
        row.addEventListener('click', function() {
            var feature = row.getAttribute('data-feature');
            var detailsRow = document.getElementById('details-' + feature);
            var arrow = row.querySelector('.feature-arrow');
            if (detailsRow) {
                var isOpen = !detailsRow.classList.contains('hidden');
                document.querySelectorAll('.feature-details-row').forEach(function(r) {
                    r.classList.add('hidden');
                });
                document.querySelectorAll('.feature-arrow').forEach(function(a) {
                    a.style.transform = '';
                });
                if (!isOpen) {
                    detailsRow.classList.remove('hidden');
                    if (arrow) arrow.style.transform = 'rotate(180deg)';
                }
            }
        });
    });
});