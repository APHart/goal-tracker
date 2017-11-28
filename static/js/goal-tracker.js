"use strict";


$(document).ready(function() {

//Sets previous goals as autocomplete data for new goal field.
function autoCompleteList(){
    $.get("/get-goals.json", function(results) {
        $("#new-goal-name").autocomplete({
            source: results
        });
    });
}
autoCompleteList();

//Inserts jquery datepicker for start date field.
$(function insertDatePicker() {
    $("#start-date").datepicker({dateFormat: 'yy-mm-dd' });
    $("#comp-date").datepicker({dateFormat: 'yy-mm-dd' });

});

//When new goal is added, adds new goal to autocomplete list.
function addGoalResult(results) {
    autoCompleteList();
    alert("Your new goal has been added!");

    if (results["add"] == true) {
        let newButton = $("<button>");
        newButton.attr("id", results.id);
        newButton.attr("name", results.name);
        newButton.attr("class", "btn btn-info active goal-btn");
        newButton.attr("data-duration", results.duration);
        newButton.attr("data-num-times", results.num_times);
        newButton.attr("data-goal-type", results.type);
        newButton.attr("data-t-id", results.id);
        newButton.attr("data-target", "#goalModal")
        newButton.innerHTML = results.name;
        newButton.append(results.name);
        $("#current-tracks").append(newButton);
    }
}

//Ajax post request for adding a new goal from new_goal_form.
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

//Show modal when goal/track button is clicked.
function showModal(evt) {
    let goalName = $(this).text();
    let num = $(this).data("num-times");
    if ($(this).data("goal-type") == "P") {
        
    };

    $("#goal-name").text(goalName);

    let track_id = $(this).data("tId");
    console.log(track_id);
    $("#track-id").val(track_id);

    $.get("/get-completions.json", {t_id: track_id}, function(results) {
    console.log(results);
    $("#curr-completions").text(results);
    })

    $("#goalModal").modal("show");
}

$(document).on("click", ".goal-btn", showModal);

//Show result of adding completion info
function addCompResult(results) {
    if (results == "Success") {
        let track_id = $("#track-id").val()

        $("#add-completion-form").trigger("reset");
        $("#comp-added").fadeIn().delay(3000).fadeOut();

        $.get("/get-completions.json", {t_id: track_id}, function(results) {
        $("#curr-completions").text(results);
    })
    }

    else if (results == "Fail") {
        alert("The completion date entered is not in the date range of the goal.");
    }

}

//Ajax request to add new completion data for user goal track
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

//Ajax request to add a friend 
//(currently must be registered user and no permission needed)
//will update in the future to allow email invites and permissions required
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
        let newButton = $("<button>");
        newButton.attr("id", results.id);
        newButton.attr("name", results.name);
        newButton.attr("class", "btn btn-info active friend-btn");
        newButton.attr("data-target", "#friendModal")
        newButton.innerHTML = results.name;
        newButton.append(results.name);
        $("#user-friends").append(newButton);
    }  
}

});
