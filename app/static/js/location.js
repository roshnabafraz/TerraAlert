document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("use-location");
    const input = document.getElementById("location");

    if (!button || !input) {
        return;
    }

    button.addEventListener("click", () => {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by this browser.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                input.value = `${latitude.toFixed(4)},${longitude.toFixed(4)}`;
            },
            () => {
                alert("Unable to retrieve your location.");
            }
        );
    });
});
