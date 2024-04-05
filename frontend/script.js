function predict() {
    // prevent the form from submitting
    function predict() {
        // prevent the form from submitting
    }
    // Get Values from the form in the index.html file
    let age = document.getElementById("ageInput").value;
    let minutes = document.getElementById("minInput").value;
    let goals = document.getElementById("glsInput").value;
    let assists = document.getElementById("assistsInput").value;
    let xG = document.getElementById("xglInput").value;
    let xAG = document.getElementById("xagInput").value;
    let npxG_xAG = document.getElementById("npxg+xagInput").value;
    let PrgC = document.getElementById("prgcInput").value;
    let PrgP = document.getElementById("prgpInput").value;
    let PrgR = document.getElementById("prgrInput").value;
    let Comp_eng = document.getElementById("plInput").value;

    // URL mit den query parameters konstruieren
    let url = `/api/predict?age=${age}&minutes=${minutes}&goals=${goals}&assists=${assists}&xG=${xG}&xAG=${xAG}&npxG_xAG=${npxG_xAG}&PrgC=${PrgC}&PrgP=${PrgP}&PrgR=${PrgR}&Comp_eng=${Comp_eng}`;

    // Fetch the prediction from the backend
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Set the prediction in the index.html file
            document.getElementById("predictionValue").innerHTML = data.Value;
        })
        .catch(error => {
            console.log(error);
        });
}

// Funktion um die Werte im Formular zurückzusetzen
function reset() {
    document.getElementById("ageInput").value = "";
    document.getElementById("minInput").value = "";
    document.getElementById("glsInput").value = "";
    document.getElementById("assistsInput").value = "";
    document.getElementById("xglInput").value = "";
    document.getElementById("xagInput").value = "";
    document.getElementById("npxg+xagInput").value = "";
    document.getElementById("prgcInput").value = "";
    document.getElementById("prgpInput").value = "";
    document.getElementById("prgrInput").value = "";
    document.getElementById("plInput").value = "";
    document.getElementById("prediction").innerHTML = "";
}
