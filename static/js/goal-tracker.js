"use strict";


$(document).ready(function() {

// Sets previous goals as autocomplete data for new goal field.
function autoCompleteList(){
    $.get("/get-goals.json", function(results) {
        $("#new-goal-name").autocomplete({
            source: results
        });
    });
}
autoCompleteList();

// Inserts jquery datepicker for start date field.
$(function insertDatePicker() {
    $("#start-date").datepicker({dateFormat: 'yy-mm-dd' });
    $("#comp-date").datepicker({dateFormat: 'yy-mm-dd' });

});

// Create chart.js for current goal/track(s) completion %
function getCurrentGoalCharts() {
    console.log("Called the js function from HTML");
}
getCurrentGoalCharts();

// When new goal is added, adds new goal to autocomplete list.
function addGoalResult(results) {

    if (results["add"] == true) {
        let newLine = $("<li></li>");
        let newButton = $("<button></button>");
        newButton.attr("id", results.id);
        newButton.attr("name", results.name);
        newButton.attr("class", "btn btn-info goal-btn");
        newButton.attr("data-duration", results.duration);
        newButton.attr("data-num-times", results.num_times);
        newButton.attr("data-goal-type", results.type);
        newButton.attr("data-t-id", results.id);
        newButton.attr("data-length", results.length)
        newButton.attr("data-target", "#goalModal")
        newButton.html(results.name + " " + results.num_times + " time(s) this " 
                       + results.length + " ");
        
        if (results.type == "L") {
            newButton.append('<a class="type-tip" data-toggle="tooltip" title="Limit: a goal for limiting or decreasing an activity by setting how many times (max) in the chosen duration that you are striving for." data-placement="right">(Limit)</a>');
        }
        else if (results.type == "P") {
            newButton.append('<a class="type-tip" data-toggle="tooltip" title="Push: a goal for increasing an activity by setting how many times you are striving for in the chosen duration." data-placement="right">(Push)</a>');
        }
        
        let newSpan = $("<span>");
        newSpan.attr("class", "comp-p");
        newSpan.text(" " + results.percent_comp + " % complete");

        newLine.append(newButton, newSpan);
        $("#current-tracks").append(newLine);
        
        $(function () {
            $('[data-toggle="tooltip"]').tooltip()
        })

        $("#add-goal-form").trigger("reset");

        autoCompleteList();
    }
}

// Ajax post request for adding a new goal from new_goal_form.
function addGoal(evt) {
    evt.preventDefault();

    let formValues = {
        "new_goal_name": $("#new-goal-name").val(),
        "goal_type": $("input[name=goal-type]:checked").val(),
        "start_date": $("#start-date").val(),
        "duration": $("input[name=duration]:checked").val(),
        "repeat": $("#repeat").val(),
        "num_times": $("#num-times").val(),
    };

    $.post("/add-goal.json", formValues, addGoalResult);
}

$("#add-goal-form").on("submit", addGoal);

// Show modal when goal/track button is clicked.
function showModal(evt) {
    $(this).addClass("active")

    let goalName = $(this).text();
    let num = $(this).data("num-times");
    // if ($(this).data("goal-type") == "P") {
        
    // };

    $("#goal-name").text(goalName);

    let track_id = $(this).data("tId");
    console.log(track_id);
    $("#track-id").val(track_id);

    $.get("/get-completions.json", {t_id: track_id}, function(results) {
    $("#curr-completions").text(results.count);
    })

    $("#goalModal").modal("show");
}

$(document).on("click", ".goal-btn", showModal);

// Show result of adding completion info
function addCompResult(results) {
    if (results == "Success") {
        let track_id = $("#track-id").val()

        $("#add-completion-form").trigger("reset");
        $("#comp-added").fadeIn().delay(3000).fadeOut();

        $.get("/get-completions.json", {t_id: track_id}, function(results) {
        $("#curr-completions").text(results.count);
        $("#comp-" + track_id).text(Number(results.percent).toFixed(0) + "%");
    })
    }
    else if (results == "Fail") {
        alert("The completion date entered is not in the date range of the goal.");
    }
}

// Ajax request to add new completion data for user goal track
function addCompletion(evt) {
    evt.preventDefault();

    let formValues = {
        "track-id": $("#track-id").val(),
        "comp-date": $("#comp-date").val(),
        "comp-loc": $("#comp-loc").val(),
        "comp-time": $("#comp-time").val(),
        "comp-notes": $("#comp-notes").val(),
    };

    $.post("/add-completion.json", formValues, addCompResult);
}

$("#new-comp-submit").on("click", addCompletion);

// Ajax request to add a friend 
// (currently must be registered user and no permission needed)
// will update in the future to allow email invites and permissions required
function addFriend(evt) {
    evt.preventDefault();

    let formValues = {
        "friend-username": $("#new-friend-name").val()
    };

    $.post("/add-friend.json", formValues, addFriendResult);
}

$("#add-friend-form").on("submit", addFriend);

function addFriendResult(results) {

     if (results["add"] == true) {
        let newLine = $("<li></li>");
        let newButton = $("<button>");
        newButton.attr("id", results.id);
        newButton.attr("name", results.name);
        newButton.attr("class", "btn btn-info active friend-btn");
        newButton.innerHTML = results.name;
        newButton.append(results.name);

        newLine.append(newButton);

        $("#current-user-friends").append(newLine);
    }
    else if (results["add"] == false) {
        alert("You are already friends with " + results.name + ".");
    } 
}

function FriendShareInfo($this) {

    let friend_name = ($this).name;
    let friend_id = ($this).id;

    let data = {
        "friend_name": friend_name,
        "friend_id": friend_id,
    };

    $.post("/friend-share-info.json", data, function (results) {
        let username = results.username;
        let friend_name = results.friend_name;
        window.location.replace("/user/" + username + "/GoalShare-" + friend_name);
    });
}

window.FriendShareInfo = FriendShareInfo;

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

});

