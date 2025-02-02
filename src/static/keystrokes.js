document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM entièrement chargé, script prêt !");

    const keystrokes = [];
    const SERVER_URL = "/api/keystrokes";

    const inputElement = document.getElementById("msg-input-wrapper");
    const sendButton = document.getElementById("send_input");

    if (!inputElement || !sendButton) {
        console.error("Erreur : Impossible de trouver msg-input ou send_input dans le DOM.");
        return;
    }

    // Capturer les frappes dans l'input msg-input
    inputElement.addEventListener("keydown", (event) => {
        if (event.repeat) return; // Ignorer les répétitions automatiques

        const timestamp = performance.now(); // Plus précis que Date.now()

        const keyData = {
            key: event.key,
            code: event.code,
            timestamp: timestamp
        };

        keystrokes.push(keyData);
        // console.log(`DEBUG: Key: ${event.key}, Timestamp: ${timestamp}`);
    });

    // Envoyer les données au serveur lorsque le bouton est cliqué
    sendButton.addEventListener("click", async () => {
        if (keystrokes.length === 0) {
            console.log("Aucune frappe à envoyer.");
            return;
        }

        try {
            const response = await fetch(SERVER_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(keystrokes)
            });

            if (!response.ok) {
                console.error("Erreur lors de l'envoi :", response.statusText);
            } else {
                console.log("Données envoyées avec succès :", keystrokes);
                keystrokes.length = 0; // Vider le tableau après envoi
            }
        } catch (error) {
            console.error("Erreur réseau :", error);
        }
    });

    console.log("Les écouteurs d'événements ont été ajoutés !");
});
