const main = () => {
  const guild_id = "773323374550188054";

  let btn = document.getElementById("list-events-btn");

  btn.addEventListener("click", (event) => {
    console.log(guild_id);
    getEvents(guild_id).then((json) => {
      let events = json["events"];
      let el = document.getElementById("events");
      for (let i = 0; i < events.length; i++) {
        let e = document.createElement("div");
        e.innerHTML = JSON.stringify(events[i]);
        el.appendChild(e);
      }
    });
  });
};

async function getEvents(guild_id) {
  return await fetch(`/api/events/${guild_id}`).then((resp) => resp.json());
}
