document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".add-to-cart-btn").forEach(button => {
        button.addEventListener("click", function () {
            const menuId = this.dataset.menuId;
            const restaurantId = this.dataset.restaurantId;
            const quantity = 1; // default, can be updated later if you allow +/- in UI

            fetch("/cart/add", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        menu_id: menuId,
        restaurant_id: restaurantId,
        quantity: quantity
    })
})
.then(response => response.json().then(data => ({ status: response.status, body: data })))
.then(result => {
    if (result.status !== 200) {
        alert("Error: " + (result.body.error || "Failed to add item"));
    } else {
        alert(result.body.message || "Item added to cart!");
    }
})
.catch(error => {
    console.error(error);
    alert("Something went wrong: " + error);
});

        });
    });
});
