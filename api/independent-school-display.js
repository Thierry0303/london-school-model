<!-- Independent School Data Display -->
<script>
  document.addEventListener("DOMContentLoaded", function() {
    const schoolData = window.schoolData;
    if (!schoolData || !schoolData.independent_data) return;
    
    const ind = schoolData.independent_data;
    const section = document.createElement("div");
    section.style.cssText = "border-left: 5px solid #D4A843; padding: 20px; background: #fffbf0; margin: 20px 0;";
    
    let html = "<h2>Independent School Information</h2>";
    if (ind.fees_annual) html += "<p><b>Annual Fees:</b> £" + ind.fees_annual.toLocaleString() + "</p>";
    if (ind.a_level_a_star_b_percent) html += "<p><b>A-Level A*-B:</b> " + ind.a_level_a_star_b_percent + "%</p>";
    if (ind.gcse_9_7_percent) html += "<p><b>GCSE 9-7:</b> " + ind.gcse_9_7_percent + "%</p>";
    if (ind.isi_inspection_status) html += "<p><b>ISI Status:</b> " + ind.isi_inspection_status + "</p>";
    if (ind.boarding) html += "<p><b>Day/Boarding:</b> " + ind.boarding + "</p>";
    
    section.innerHTML = html;
    
    const examSection = document.querySelector("h2");
    if (examSection && examSection.parentNode) {
      examSection.parentNode.insertBefore(section, examSection.nextSibling);
    } else {
      document.body.appendChild(section);
    }
  });
</script>
