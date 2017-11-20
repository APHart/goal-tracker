"use strict";


//Sets previous goals as autocomplete data for new goal field.
function autoCompleteList(){
    $.get("/get-goals.json", function(results) {
        $("#new_goal_name").autocomplete({
            source: results
        });
    });
}

$(document).ready(autoCompleteList());

//Inserts jquery datepicker for start date field.
$(function insertDatePicker() {
    $("#start_date").datepicker({dateFormat: 'yy-mm-dd' });

});

//When new goal is added, adds new goal to autocomplete list.
function addGoalResult() {
    autoCompleteList();
    alert("Your new goal has been added!");
}

//Ajax post request for adding a new goal from new_goal_form.
function addGoal(evt) {
    evt.preventDefault();

    let formValues = {
        "new_goal_name": $("#new_goal_name").val(),
        "goal_type": $("#goal_type").val(),
        "start_date": $("#start_date").val(),
        "duration": $("#duration").val(),
        "repeat": $("#repeat").val(),
        "num_times": $("#num_times").val(),
    };

    console.log("in addGoal");

    $.post("/add-goal.json", formValues, addGoalResult);
}

$("#add_goal_submit").click(addGoal);

//Show modal when goal/track button is clicked.
function showModal(evt) {
    let goalName = $(this).text();
    $("#goal-name").text(goalName);

    let track_id = $(this).data("t-id");
    console.log(track_id);

    $.get("/get-completions.json", {t_id: track_id}, function(results) {
    console.log(results);
    $("#curr-completions").text(results);
    })

    $("#goalModal").modal("show");
}

$(".goal-btn").click(showModal);
