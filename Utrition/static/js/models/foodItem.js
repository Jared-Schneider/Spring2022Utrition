
// Contains the information pertaining to a single food item that the user has entered into the addFood partial
// Will make it easier to abstract away the underlying stuff for cleaner code in other parts of the project
class foodItem {
    internal_id; // an integer. *for internal use on the frontend only*
        // it's just a number we store to identify each food entered
        // Starts at 1. and increments by 1 everytime a new food is created
    group;
    item;
    quantity;
    unit;

    static id = 1;  
    // static variables are associated with an entire class, not a particular instance
    // They exist only once in memory. Access them like <className>.<staticVarName>, not off of an object
    // So here, id is accesed like foodItem.id 

    constructor(newGroup,newItem,newQuantity,newUnit, newFoodID) {
        this.internal_id = foodItem.id;
        foodItem.id = foodItem.id + 1;
        this.food_id = newFoodID;
        this.group = newGroup;
        this.item = newItem;
        this.quantity = newQuantity;
        this.unit = newUnit;
    }

    // Returns a paragraph element for describing the food
    describeFood() {
        let foodDesc = document.createElement('p');
        foodDesc.innerHTML = this.item +  ", " + this.quantity + " " + this.unit;
        return foodDesc;
    }


    // --- Getters ---
    getGroup() {
        return this.group;
    }
    getItem() {
        return this.item;
    }
    getQuantity() {
        return this.quantity;
    }
    getUnit() {
        return this.unit;
    }

    // --- Setters ---
    setGroup(newGroup) {
        this.group = newGroup;
    }
    setItem(newItem) {
        this.item = newItem;
    }
    setQuantity(newQuantity) {
        this.quantity = newQuantity;
    }
    setUnit(newUnit) {
        this.unit = newUnit;
    }
}