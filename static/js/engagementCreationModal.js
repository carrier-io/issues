const EngagementCreationModal = {
    emits: ['added'],
    data() {
        return {
            formId: "#eng-form-create",
            tableId: "#engagement-table",
            modalId: "#eng_create_modal",
        }
    },
    mounted(){
        $(this.modalId).on("show.bs.modal", () => {
            $(this.formId).get(0).reset();
        });
    },
    methods: {
        save() {
            data = $(this.formId).serializeObject();
            axios.post(engagements_list, data)
                .then(() => {
                    this.$emit('added')
                    $(this.modalId).modal("hide");
                    showNotify("SUCCESS", 'Successfully created')
                })
                .catch(err => {
                    console.log(err)
                })
        }
    },
    template: `
        <button type="button"
            data-toggle="modal" 
            data-target="#eng_create_modal"
            class="btn btn-secondary btn-sm btn-icon__sm"
        >
            <i class="fas fa-plus"></i>
        </button>

        <div id="eng_create_modal" class="modal modal-small fixed-left fade shadow-sm" tabindex="-1" role="dialog">
            <div class="modal-dialog modal-dialog-aside" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <div class="row w-100">
                            <div class="col">
                                <h2>Create  Engagement</h2>
                            </div>
                            <div class="col-xs">
                                <button type="button" class="btn  btn-secondary mr-2" data-dismiss="modal" aria-label="Close">
                                    Cancel
                                </button>
                                <button type="button" @click="save" class="btn btn-basic">Save</button>
                            </div>
                        </div>
                    </div>
                    <div class="modal-body">
                        <form id="eng-form-create">
                            <div class="section p-1">
                                <div class="custom-input mb-3">
                                    <label for="input-name" class="font-weight-bold mb-1">Engagement Name</label>
                                    <input type="text" name="name" id="input-name">
                                </div>
            
                                <div class="custom-input mb-3">
                                    <label for="text-goal" class="font-weight-bold mb-1">Goal</label>
                                    <textarea class="form-control" name="goal" rows="8" id="text-goal"></textarea>
                                </div>

                                <div class="mb-3">
                                    <label for="text-goal" class="font-weight-bold mb-1">Status</label>
                                    <div class="d-flex">
                                        <select class="selectpicker bootstrap-select__b flex-grow-1" data-style="btn">
                                            <option value="new">New</option>
                                            <option value="in_progress">In Progress</option>
                                            <option value="done">Done</option>
                                        </select>
                                    </div>
                                </div>  

                                <div class="row">
                                    <div class="col">
                                        <div class="form-group">
                                            <label for="start_date" class="font-weight-bold mb-1">Start Date</label>
                                            <input type="date" name="start_date" class="form-control">
                                        </div>
                                    </div>
                                    <div class="col">
                                        <div class="form-group">
                                            <label for="end_date" class="font-weight-bold mb-1">End Date</label>
                                            <input type="date" name="end_date" class="form-control">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `
}
