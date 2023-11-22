// Delete a listing by its id value
document.querySelector(".delete").addEventListener("click", (e) => {
  const confirm = window.confirm("Are you sure?");

  if (confirm) {
    const listigId = document.querySelector(".delete").dataset.id;

    fetch(`/delete/${listigId}`).then((res) => {
      window.location.replace("/");
    });
  }
});
