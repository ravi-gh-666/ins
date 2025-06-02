const t = window.TRANSLATIONS || {};
function tr(key) {
  return t[key] || key;
}

function renderScorecard(data) {
    // ...existing code from previous script...
    if (!data || !data.policy_data || !data.policy_data.InsurerDetails) {
        return `<div class="card bg-red-50 text-center text-red-700 font-semibold py-8">${tr("No policy available for the selected insurer.")}</div>`;
    }
    const d = data;
    const insurer = d.policy_data.InsurerDetails;
    const scores = d.scores;
    function scoreRing(val) {
        let color = val <= 5 ? '#e53935' : (val < 8 ? '#ffa000' : '#43a047');
        let percent = (val / 10) * 100;
        let circ = 2 * Math.PI * 24;
        let offset = (1 - percent / 100) * circ;
        return `<span class='score-ring' style='display:inline-block;width:54px;height:54px;position:relative;vertical-align:middle;'>
            <svg width='54' height='54' style='transform:rotate(-90deg);'>
                <circle cx='27' cy='27' r='24' fill='none' stroke='#eee' stroke-width='6'/>
                <circle cx='27' cy='27' r='24' fill='none' stroke='${color}' stroke-width='6' stroke-dasharray='${circ}' stroke-dashoffset='${offset}' stroke-linecap='round'/>
            </svg>
            <span class='score-text' style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:1.3em;font-weight:700;color:#222;'>${val}</span>
        </span>`;
    }
    function tag(val) {
        let tagText = val;
        let c = 'red';
        if (typeof tagText === 'string') {
            if (tagText.includes('Good') || tagText.trim().toLowerCase() === 'yes') {
                c = 'green';
            } else if (tagText.includes('Decent')) {
                c = 'orange';
            }
        }
        return `<span class='tag ${c}' style='margin-left:8px;'>${tagText}</span>`;
    }
    function featureYoutubeEmbed(feature) {
        if (feature.youtube_video) {
            const videoId = feature.youtube_video.split('youtu.be/').pop();
            return `<div class="flex-shrink-0 flex items-center justify-center w-full md:w-[360px] mt-4 md:mt-0">
                <div style="background:#fff; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.07); width:100%; max-width:360px; aspect-ratio:16/9; display:flex; align-items:center; justify-content:center;">
                    <iframe src="https://www.youtube.com/embed/${videoId}" title="YouTube video" frameborder="0" allowfullscreen style="width:100%; height:100%; border:none; border-radius:12px;"></iframe>
                </div>
            </div>`;
        }
        return '';
    }
    let html = `
    <div class='card bg-white rounded-lg shadow p-6'>
        <div class='flex flex-col md:flex-row gap-6 items-stretch'>
            <div class='bg-white rounded-xl shadow p-6 flex flex-col justify-center' style='flex-basis:80%;flex-grow:1;max-width:80%;'>
                <h4 style='font-size:1.13rem;font-weight:600;color:#222;margin-bottom:0.7rem;text-align:left;'>${tr("Insurer Scores")}</h4>
                <div style='font-size:1rem;color:#222;margin-bottom:1.2em;line-height:1.7;text-align:left;'><strong>${tr("Insurer:")}</strong> ${insurer.Insurer}</div>
                <p style='font-size:1rem;color:#222;line-height:1.7;margin-bottom:1.1em;text-align:left;'><strong>${tr("3 Year Average CSR:")}</strong> ${insurer.ThreeYearAverageCSR.Value} ${tag(insurer.ThreeYearAverageCSR.Tag)}</p>
                <p style='font-size:1rem;color:#222;line-height:1.7;margin-bottom:1.1em;text-align:left;'><strong>${tr("Network Hospitals:")}</strong> ${insurer.NetworkHospitals.Value} ${tag(insurer.NetworkHospitals.Tag)}</p>
                <p style='font-size:1rem;color:#222;line-height:1.7;margin-bottom:1.1em;text-align:left;'><strong>${tr("Volume of Complaints:")}</strong> ${insurer.VolumeOfComplaints.Value} ${tag(insurer.VolumeOfComplaints.Tag)}</p>
                <p style='font-size:1rem;color:#222;line-height:1.7;margin-bottom:1.1em;text-align:left;'><strong>${tr("Solvency Ratio:")}</strong> ${insurer.SolvencyRatio.Value} ${tag(insurer.SolvencyRatio.Tag)}</p>
                <p style='font-size:1rem;color:#222;line-height:1.7;margin-bottom:1.1em;text-align:left;'><strong>${tr("Pay-Out Ratio:")}</strong> ${insurer.PayOutRatio.Value} ${tag(insurer.PayOutRatio.Tag)}</p>
            </div>
            <div class='bg-white rounded-xl shadow p-6 flex flex-col justify-center items-center' style='flex-basis:20%;flex-grow:0;max-width:20%;min-width:180px;'>
                <h4 style='font-size:1.13rem;font-weight:600;color:#222;margin-bottom:0.7rem;text-align:left;'>${tr("Policy Scores")}</h4>
                <div style='font-size:1.08rem;color:#222;margin-bottom:1.2em;text-align:left;'><strong>${tr("Policy:")}</strong> ${insurer.InsurancePolicy}</div>
                <div class='flex flex-col gap-3 w-full max-w-[220px] mx-auto'>
                    <div class='flex items-center justify-between gap-3'><span style='font-size:1.08rem;color:#222;font-weight:500;'>${tr("Overall")}</span>${scoreRing(scores.overall_score)}</div>
                    <div class='flex items-center justify-between gap-3'><span style='font-size:1.08rem;color:#222;font-weight:500;'>${tr("Insurer")}</span>${scoreRing(scores.insurer_rating)}</div>
                    <div class='flex items-center justify-between gap-3'><span style='font-size:1.08rem;color:#222;font-weight:500;'>${tr("Features")}</span>${scoreRing(scores.feature_rating)}</div>
                    <div class='flex items-center justify-between gap-3'><span style='font-size:1.08rem;color:#222;font-weight:500;'>${tr("Affordability")}</span>${scoreRing(scores.affordability_rating)}</div>
                </div>
            </div>
        </div>
    </div>
    ${((d.policy_data.Pros && d.policy_data.Pros.length) || (d.policy_data.Cons && d.policy_data.Cons.length)) ? `
    <div class='flex flex-col md:flex-row gap-6 items-stretch mb-8 mt-6'>
        <div class='flex-1 bg-green-50 rounded-lg p-6'>
            <h4 class='font-bold text-green-700 mb-2'>${tr("Pros")}</h4>
            <ul>
                ${(d.policy_data.Pros||[]).map(pro=>`<li>✔️ ${pro}</li>`).join('')}
            </ul>
        </div>
        <div class='flex-1 bg-red-50 rounded-lg p-6'>
            <h4 class='font-bold text-red-700 mb-2'>${tr("Cons")}</h4>
            <ul>
                ${(d.policy_data.Cons||[]).map(con=>`<li>❌ ${con}</li>`).join('')}
            </ul>
        </div>
    </div>
    ` : ''}
    <div class='card bg-white rounded-lg shadow p-6 mt-6'>
        <h2 style='font-size:0.85rem;letter-spacing:0.08em;font-weight:500;color:#5f6368;text-transform:uppercase;margin-bottom:0.5rem;'>${tr("Policy Features")}</h2>
        <h3 style='font-size:2rem;font-weight:400;color:#202124;margin-bottom:1.2rem;'>${tr("Mandatory Features")}</h3>
        ${(d.mandatory_features||[]).map(f=>`<div class='card bg-gray-50 rounded-lg shadow-sm p-4 mb-4 flex flex-col md:flex-row gap-6 items-stretch'><div class='flex-1 flex flex-col justify-center'><div class='feature-title flex items-center text-base font-semibold mb-2'><span class='material-icons feature-icon text-blue-700 mr-2'>verified_user</span>${f.FeatureName}</div><p class='mb-1'><strong>${tr("Offered:")}</strong> <span class='tag ${f.FeatureOffered=="Yes"?"green":(f.FeatureOffered=="No"?"red":"orange")}' style='margin-left:8px;'>${f.FeatureOffered}</span></p><div class='explanation text-gray-700 mb-1'>${f.Explanation||''}</div><div class='details text-gray-600 mb-1'><strong>${tr("Details:")}</strong> ${f.Details||''}</div><div class='why-matters text-blue-700 italic mb-1'><strong>${tr("Why this matters:")}</strong> ${f.why_matters||''}</div><div class='caveats text-red-600 mb-1'><strong>${tr("Caveats:")}</strong> ${f.Caveats||''}</div></div>${featureYoutubeEmbed(f)}</div>`).join('')}
        <h3 style='font-size:2rem;font-weight:400;color:#202124;margin-bottom:1.2rem;'>${tr("Good To Have Features")}</h3>
        ${(d.good_features||[]).map(f=>`<div class='card bg-gray-50 rounded-lg shadow-sm p-4 mb-4 flex flex-col md:flex-row gap-6 items-stretch'><div class='flex-1 flex flex-col justify-center'><div class='feature-title flex items-center text-base font-semibold mb-2'><span class='material-icons feature-icon text-teal-600 mr-2'>star_rate</span>${f.FeatureName}</div><p class='mb-1'><strong>${tr("Offered:")}</strong> <span class='tag ${f.FeatureOffered=="Yes"?"green":(f.FeatureOffered=="No"?"red":"orange")}' style='margin-left:8px;'>${f.FeatureOffered}</span></p><div class='explanation text-gray-700 mb-1'>${f.Explanation||''}</div><div class='details text-gray-600 mb-1'><strong>${tr("Details:")}</strong> ${f.Details||''}</div><div class='why-matters text-blue-700 italic mb-1'><strong>${tr("Why this matters:")}</strong> ${f.why_matters||''}</div><div class='caveats text-red-600 mb-1'><strong>${tr("Caveats:")}</strong> ${f.Caveats||''}</div></div>${featureYoutubeEmbed(f)}</div>`).join('')}
        <button class='action-btn'>${tr("Get Quote")}</button>
    </div>`;
    return html;
}
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.top-plan-row').forEach(function(row) {
        row.addEventListener('click', function() {
            const insurer = this.getAttribute('data-insurer');
            const policy = this.getAttribute('data-policy');
            if (!insurer || !policy) return;
            fetch(`/api/scorecard_by_name?insurer=${encodeURIComponent(insurer)}&policy=${encodeURIComponent(policy)}`)
                .then(res => res.json())
                .then(data => {
                    const section = document.getElementById('scorecard-section');
                    section.innerHTML = renderScorecard(data);
                    section.style.display = '';
                    section.scrollIntoView({behavior:'smooth', block:'start'});
                });
        });
    });
});
