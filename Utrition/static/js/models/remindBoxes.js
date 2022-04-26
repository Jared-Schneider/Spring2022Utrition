
// Responsible for the popup on the addFoods partial
class remindBoxes {


    constructor() {
        // List of each reminder
        // If changing the number of items, change the hardcoded number within createEvents()
        //      Changing this to a class level static variable should be able to fix this hardcode problem
        this.boxes = [
        "Cereals, Breads, Snacks",
        "Meat, Fish, Eggs",
        "Spaghetti, Mixed Dishes, Soups",
        "Dairy Products",
        "Vegetables and Grains",
        "Sauces and Condiments",
        "Fruits",
        "Sweets",
        "Beverages and Alcohol"
        ]
        this.goToFinish = document.getElementById('finishAnchor');
        this.holder = document.getElementById('reminderHolder');
        this.createReminder();
        this.doneBtn = document.getElementById('cont');
        this.doneBtn.disabled = true;

        this.visibility(false);
    }


    checkDone() {


    }

    // Creates the list of reminders dynamically
    // Done this way to make it easier for the text to be changed later
    // Sample:
    // <div class=singleFood>
    //      <div class=foodLabel> <p>label</p> </div>
    //      <div class=checkboxes> <input form=checkbox>yes <input form=checkbox> no </div>
    createReminder() {
        let h = document.getElementById('reminders');
        for (let i = 0; i<this.boxes.length; i++) {
            // Create all of the divs
            let checkboxDiv = document.createElement('div');
            checkboxDiv.className = "checkboxes";
            let labelDiv = document.createElement('div');
            labelDiv.className = "foodLabel";
            let reminderDiv = document.createElement('div');
            reminderDiv.className = "reminderDiv";

            // Create the label - goes in the labelDiv
            let currLabel = document.createElement('p');
            currLabel.for = i;
            currLabel.innerHTML = this.boxes[i];
            currLabel.className = "reminderLabel";

            labelDiv.appendChild(currLabel);


            // Create the Checkboxes - go in the checkbox div
            let currInputNo = document.createElement('input');
            currInputNo.id = i + 'No';
            currInputNo.type = "radio";
            currInputNo.name = i;
            currInputNo.value = this.boxes[i];


            let currInputYes = document.createElement('input');
            currInputYes.type = "radio"
            currInputYes.name = i;
            currInputYes.id = i + 'Yes';
            currInputYes.className = "reminderInput";
            checkboxDiv.appendChild(currInputYes);
            checkboxDiv.appendChild(currInputNo);

            // Assemble the box
            reminderDiv.appendChild(labelDiv);
            reminderDiv.appendChild(checkboxDiv);
            h.appendChild(reminderDiv);
        }
        this.createEvents();
    }

    // Private function that sets the events for the checkboxes
    // Needed for the complete form button to be dynamically enabled/disabled

    createEvents() {
        // Events for all of the 'Yes' radio boxes
        for (let i = 0; i<this.boxes.length; i++) {
            let currBox = document.getElementById(i + 'Yes');
            currBox.addEventListener('click', function() {
                let isDone = 1;
                for (let j = 0; j<9; j++) {
                    let checkingBox = document.getElementById(j + 'Yes');
                    if (!checkingBox.checked) {
                        isDone = 0;
                    }

                }

                if (isDone == 1) {
                    // All boxes are checked
                    document.getElementById('cont').disabled = false;
                }
            });
        }

        // Events for all of the 'No' radio boxes
        for (let i = 0; i<this.boxes.length; i++) {
            let currBox = document.getElementById(i + 'No');
            currBox.addEventListener('click', function() {
               if (currBox.checked) {
                    let newParagraph = document.getElementById('forgottenParagraph');
                    if (newParagraph == null) {
                        // Create the reminder paragraph above the meal time drop down of what food the user forgot
                        let newParagraph = document.createElement('p');
                        newParagraph.id = 'forgottenParagraph';
                        newParagraph.innerHTML = 'Please add any ' + currBox.value + ' you may have forgotten.';
                        let directions = document.getElementById('addFoodDirections');
                        directions.after(newParagraph);
                    }
                    else {
                        newParagraph.innerHTML = 'Please add any ' + currBox.value + ' you may have forgotten.';
                    }
                    document.getElementById('reminderHolder').style = "display:none";
                }
            });
        }
    }

    // Sets the visibility of the food reminder list
    // display:block allows the list to be shown
    visibility(isOn) {
        if (isOn) {
            this.holder.style = "display:block";
        }
        else {
            this.holder.style = "display:none";
        }
    }

}