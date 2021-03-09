const main = () => {
  setupAddEventsPopup();
};

const setupAddEventsPopup = () => {
  let addEventBtn = document.getElementById("add-event-btn");
  let addEventPopup = document.getElementById("add-event-modal");
  let closeBtn = document.getElementById("close-add-event-modal");
  const close = () => {
    addEventPopup.style.display = "none";
    addEventBtn.addEventListener("click", addEvent);
  };
  const addEvent = (ev) => {
    addEventPopup.style.display = "block";
    addEventBtn.removeEventListener("click", addEvent);
    closeBtn.addEventListener("click", close);
  };
  addEventBtn.addEventListener("click", addEvent);
};

const addListEventsStuff = () => {
  const guild_id = "";

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

function toggleColor() {
  var toggle = document.getElementById("toggle");
  console.log(toggle);
  console.log(toggle.style);
  //toggle.setAttribute("fill", "white");
  //toggle.style.fill = "#253039";
  // toggle[1].style.fill = "#253039";
  // toggle[2].style.fill = "#253039";
  // toggle[3].style.fill = "#ffffff";
}

async function getEvents(guild_id) {
  return await fetch(`/api/events/${guild_id}`).then((resp) => resp.json());
}
