const main = () => {};
const guild_id = 773323374550188054;
console.log("hello there.");
let btn = document.getElementById("list-events-btn");
btn.addEventListener("click", (event) => {
  fetch(`/api/events/${guild_id}`)
    .then((resp) => resp.json())
    .then((json) => {
      let events = json["events"];
      let el = document.getElementById("events");
      for (let i = 0; i < events.length; i++) {
        let e = document.createElement("div");
        e.innerHTML = JSON.stringify(events[i]);
        el.appendChild(e);
      }
    });
});
