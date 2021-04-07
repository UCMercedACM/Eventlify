const TOKEN_COOKIES = [
  "guild_id",
  "access_token",
  "expires_in",
  "refresh_token",
  "scope",
  "token_type",
];

const main = () => {
  let cookie = getCookies();
  let app = new App(cookie.guild_id, new Token(cookie));

  setupAddEventsPopup(app);
  applyLogoutHandler();
};

const setupAddEventsPopup = (app) => {
  let addEventBtn = document.getElementById("add-event-btn");
  let addEventPopup = document.getElementById("add-event-modal");
  let closeBtn = document.getElementById("close-add-event-modal");
  let saveBtn = document.getElementById("save-new-event");
  const close = () => {
    addEventPopup.style.display = "none";
    addEventBtn.addEventListener("click", addEventDisplay);
  };

  const saveEvent = () => {
    let newEvent = parseEvent();
    console.log("event input:", newEvent);
    app.addEvent(newEvent);
  };

  const addEventDisplay = (ev) => {
    addEventPopup.style.display = "block";
    addEventBtn.removeEventListener("click", addEventDisplay);
    closeBtn.addEventListener("click", close);
  };
  if (addEventBtn === null) {
    return;
  }

  addEventBtn.addEventListener("click", addEventDisplay);
  saveBtn.addEventListener("click", saveEvent);
};

function parseEvent() {
  var date = new Date();

  var time = "" + document.getElementById("new-event-time").value;
  var split = time.split(":");
  date.setHours(parseInt(split[0]));
  date.setMinutes(parseInt(split[1]));

  // TODO this makes the date "Invalid Date", fix it
  date.setDate(document.getElementById("new-event-date").valueAsDate);

  /*document
    .getElementById("new-event-date")
    .addEventListener("change", function () {
      var input = this.value;
      date.setDate(input);
    });
  */
  var title = document.getElementById("new-event-title").value;
  var description = document.getElementById("new-event-desc").value;

  console.log("input date:", date);
  return {
    name: title,
    date: date,
    description: description,
  };
}

const applyLogoutHandler = () => {
  let btn = document.getElementById("logout-btn");
  const callback = () => {
    // btn.removeEventListener("click", callback);
    logout();
    window.location.pathname = "/";
  };
  if (btn === null) {
    return;
  }
  btn.addEventListener("click", callback);
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
  var toggle = document.getElementById("toggleColor");
  console.log(toggle);
  console.log(toggle.style);
  //toggle.setAttribute("fill", "white");
  //toggle.style.fill = "#253039";
  // toggle[1].style.fill = "#253039";
  // toggle[2].style.fill = "#253039";
  // toggle[3].style.fill = "#ffffff";
}

// dummy function for commands

function toggleCommand() {
  let elist = document.getElementById("toggleEList");
  let eadd = document.getElementById("toggleEAdd");
  let eremove = document.getElementById("toggleERemove");
  let eedit = document.getElementById("toggleEEdit");

  let callback = function (event) {
    // put stuff here
  };

  elist.addEventListener("click", function (event) {
    if (event.currentTarget == elist) {
      console.log("you toggled e!list");
    } else if (event.currentTarget == eadd) {
      console.log("you togged e!add");
    } else if (event.currentTarget == eremove) {
      console.log("you toggled e!remove");
    } else {
      console.log("you toggled e!edit");
    }
    //console.log("yee", event);
  });
}

//togglecommand

async function getEvents(guild_id) {
  return await fetch(`/api/events/${guild_id}`).then((resp) => resp.json());
}

function getCookies() {
  let res = {};
  document.cookie.split(/\s*;\s*/).forEach(function (pair) {
    pair = pair.split(/\s*=\s*/);
    res[pair[0]] = pair.splice(1).join("=");
  });
  return res;
}

function logout() {
  for (let name of TOKEN_COOKIES) {
    console.log("clearing", name);
    clearCookie(name);
  }
}

function loggedIn() {
  let cookies = getCookies();
  return cookies.hasOwnProperty("token");
}

async function token() {
  let cookie = getCookies();
  let params = new URLSearchParams({
    grant_type: "authorization_code",
    code: cookie.discord_code,
  });
  return fetch("https://discord.com/api/oauth2/token", {});
}

// NOTE: This will not clear cookies with HttpOnly set and will
// not clear cookies with the Path value set.
function clearCookie(name) {
  // This is really gross, but works
  // https://stackoverflow.com/questions/179355/clearing-all-cookies-with-javascript
  document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
}

class App {
  constructor(guild_id, token) {
    if (guild_id === undefined) {
      // user is not signed in
      throw Error("no guild id");
    }
    this.guild_id = guild_id;
    this.token = token;
  }

  async events() {
    return fetch(`/api/events/${this.guild_id}`)
      .then((resp) => {
        if (resp.ok) {
          return resp.json();
        }
        // TODO: Handle error
      })
      .then((events) => events["events"]);
  }

  async addEvent(event) {
    console.log("sending event:", event);
    return fetch(`/api/event`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: event.name,
        date: event.date, // TODO format this
        description: event.description,
        guild_id: this.guild_id,
      }),
    })
      .then((resp) => {
        if (resp.ok) {
          return;
        }
        // TODO error handling
        console.log(resp);
        console.log("could not add event:", resp.body);
        let contentType = resp.headers.get("content-type");
        if (contentType === "application/json") {
          return resp.json();
        }
      })
      .then((jsonMsg) => console.log(jsonMsg));
  }

  async me() {
    return fetch("https://discord.com/api/users/@me", {
      headers: {
        Authorization: `${this.token.token_type} ${this.token.access_token}`,
      },
    })
      .then((resp) => {
        if (resp.ok) {
          return resp.json();
        } else {
          throw Error("could not get current user");
        }
      })
      .then((json) => new User(json));
  }
}

class Event {
  constructor(name, date, description) {
    if (
      typeof name === "object" &&
      date === undefined &&
      description === undefined
    ) {
      Object.assign(this, name);
    } else {
      this.name = name;
      this.date = date;
      this.description = description;
    }
  }
}

class User {
  constructor(data) {
    Object.assign(this, data);
  }

  // TODO discord api stuff
}

class Token {
  constructor(cookie) {
    if (cookie === undefined) {
      cookie = getCookies();
    }
    this.access_token = cookie.access_token;
    this.refresh_token = cookie.refresh_token;
    this.expires_in = cookie.expires_in;
    this.scope = cookie.scope;
    this.token_type = cookie.token_type;
  }
}
