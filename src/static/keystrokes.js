document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM entièrement chargé, script prêt !");

    const keystrokes = [];
    const KEYSTROKE_ENDPOINT = "/api/keystrokes";

    const inputElement = document.getElementById("msg-input-wrapper");
    const sendButton = document.getElementById("send_input");

    if (!inputElement || !sendButton) {
        console.error("Erreur : Impossible de trouver msg-input ou send_input dans le DOM.");
        return;
    }

    // Capturer les frappes dans l'input msg-input
    inputElement.addEventListener("keydown", (event) => {
        // if (event.repeat) return; // Ignorer les répétitions automatiques

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
        try {
            const keyData = {
                key: document.getElementById("msg-input").value || "empty",
                code: "MsgSent",
                timestamp: performance.now()
            };
            keystrokes.push(keyData);
        } catch (error) {
            console.error("Error while inserting fake keystroke :", error);
        }

        try {
            const response = await fetch(KEYSTROKE_ENDPOINT, {
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

    const chatlist_container = document.getElementById("chatlist");
    const container_tutor = document.getElementById("tutor_history_content");


    // Fonction pour faire défiler en bas
    function scrollToBottom(what) {
        what.scrollTop = what.scrollHeight;
        setTimeout(() => {
            what.scrollTop = what.scrollHeight;
        }, 1100); // Petit délai pour laisser le DOM se mettre à jour
    }

// Observer les ajouts d'éléments dans la div
    const observer = new MutationObserver(() => {
        scrollToBottom(chatlist_container);
    });
    observer.observe(chatlist_container, {childList: true});


    const observer_tutor = new MutationObserver(() => {
        scrollToBottom(container_tutor);
    });
    observer_tutor.observe(container_tutor, {childList: true});


    console.log("Les écouteurs d'événements ont été ajoutés !");
});
