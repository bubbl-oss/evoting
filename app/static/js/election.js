if (document.getElementById("datetime_picker")) {
  const times_input = document.getElementById("times_input");
  const unit_select = document.getElementById("unit_select");
  const starting_at_input = document.getElementById("starting_at");
  const ending_at_input = document.getElementById("ending_at");
  const ending_at_display = document.getElementById("ending_at_display");
  const datetime_input = document.getElementById("datetime_input");
  const datetime_input_block = document.getElementById("datetime_input_block");

  // the unit default is max=7 for hours. but then the user changes the unit
  // we likewise change the max on the times_input, then we change the value of the ending_at input to
  // the corresponding value

  starting_at_input.addEventListener("input", function (e) {
    // reset the whole time thing...

    // debugger;

    // var last_ending_at_value = ending_at_input.value;
    // setInterval(function () {
    //   var newValue = ending_at_input.value;
    //   if (last_ending_at_value != newValue) {
    //     last_ending_at_value = newValue;
    //     handleValueChange();
    //   }
    // }, 50); // 20 times/second
    // function handleValueChange() {
    //   console.log("$input's value changed: " + ending_at_input.value);
    // }

    const time = moment(e.target.value).add(
      times_input.value,
      unit_select.value
    );

    // Rounding minute on 30 mins interval
    // from... https://stackoverflow.com/a/61117519/10382407
    // if (minute <= 30 && unit_select.value != "m") time.set({ minute: 30 });
    // if (minute > 30 && unit_select.value != "m") time.set({ minute: 0 });

    if (
      unit_select.value != "m" &&
      unit_select.value != "h" &&
      datetime_input.value
    ) {
      time.set({
        hour: datetime_input.value.split(":")[0],
        minute: datetime_input.value.split(":")[1],
      });
    }

    ending_at_input.value = time.format("Y-MM-DDTHH:mm");

    ending_at_display.innerText = "On " + time.format("lll");
  });

  unit_select.addEventListener("change", function (e) {
    // debugger;

    times_input.value = "";
    ending_at_input.value = "";
    ending_at_display.innerText = "";

    if (e.target.value != "m" && e.target.value != "h") {
      datetime_input_block.style.display = "flex";
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
    if (unit_select.value != "m" && unit_select.value != "h") {
      // debugger;

      let time = moment(ending_at_input.value);

      let datetime_input_time = datetime_input.value;

      time.set({
        hour: datetime_input_time.split(":")[0],
        minute: datetime_input_time.split(":")[1],
      });

      ending_at_input.value = time.format("Y-MM-DDTHH:mm");

      ending_at_display.innerText = "On " + time.format("lll");
    }
  });

  // TODO: llok at that alpine.js mutation obeerbr o

  times_input.addEventListener("input", function (e) {
    // when the user inputs a new time...
    // debugger;

    const starting_at_time = starting_at_input.value || new Date();

    const time = moment(starting_at_time).add(
      e.target.value,
      unit_select.value
    );

    // Rounding minute on 30 mins interval
    // from... https://stackoverflow.com/a/61117519/10382407
    // if (minute <= 30 && unit_select.value != "m") time.set({ minute: 30 });
    // if (minute > 30 && unit_select.value != "m") time.set({ minute: 0 });

    if (
      unit_select.value != "m" &&
      unit_select.value != "h" &&
      datetime_input.value
    ) {
      time.set({
        hour: datetime_input.value.split(":")[0],
        minute: datetime_input.value.split(":")[1],
      });
    }

    ending_at_input.value = time.format("Y-MM-DDTHH:mm");

    ending_at_display.innerText = "On " + time.format("lll");
  });
}
