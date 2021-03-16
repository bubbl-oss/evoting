if (document.getElementById("datetime_picker")) {
  const times_input = document.getElementById("times_input");
  const unit_select = document.getElementById("unit_select");
  const ending_at_input = document.getElementById("ending_at");
  const ending_at_display = document.getElementById("ending_at_display");
  const datetime_input = document.getElementById("datetime_input");
  const datetime_input_block = document.getElementById("datetime_input_block");

  // the unit default is max=7 for hours. but then the user changes the unit
  // we likewise change the max on the times_input, then we change the value of the ending_at input to
  // the corresponding value

  unit_select.addEventListener("change", function (e) {
    times_input.value = "";
    ending_at_input.value = "";
    ending_at_display.innerText = "";

    if (e.target.value != "m" && e.target.value != "h") {
      datetime_input_block.style.display = "inline-block";
    } else {
      datetime_input_block.style.display = "none";
    }

    switch (e.target.value) {
      case "m":
        // hours
        times_input.step = "15";
        times_input.max = "45";
        times_input.min = "15";

        break;
      case "h":
        // hours
        times_input.min = "1";
        times_input.max = "23";
        times_input.step = "1";

        break;
      case "d":
        // days
        times_input.min = "1";
        times_input.max = "7";
        times_input.step = "1";

        break;
      case "w":
        // weeks
        times_input.min = "1";
        times_input.max = "4";
        times_input.step = "1";

        break;
      default:
        break;
    }
  });

  datetime_input.addEventListener("input", function (e) {
    if (e.target.value != "m" && e.target.value != "h") {
      const time = moment(ending_at_input.value);

      const datetime_input_time = datetime_input.value;

      time.set({
        hour: datetime_input_time.split(":")[0],
        minute: datetime_input_time.split(":")[1],
      });

      ending_at_input.value = time.format("Y-MM-DDTH:mm");

      ending_at_display.innerText = "On " + time.format("lll");
    }
  });

  times_input.addEventListener("input", function (e) {
    // when the user inputs a new time...

    const time = moment().add(e.target.value, unit_select.value);

    // Rounding minute on 30 mins interval
    // from... https://stackoverflow.com/a/61117519/10382407
    // if (minute <= 30 && unit_select.value != "m") time.set({ minute: 30 });
    // if (minute > 30 && unit_select.value != "m") time.set({ minute: 0 });

    ending_at_input.value = time.format("Y-MM-DDTH:mm");

    ending_at_display.innerText = "On " + time.format("lll");
  });
}
