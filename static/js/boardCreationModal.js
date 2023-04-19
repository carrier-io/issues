const BoardCreationModal = {
    props: ['queryUrl', 'engagement'],
    data() {
        return {
            modal_id: "#board_create_modal",
            create_modal_form_id: '#board-form-create',
            defaultValues:{
                "state_update_url": "{{secret.galloper_url}}/api/v1/issues/issue/{{secret.project_id}}",
                "tickets_url": "{{secret.galloper_url}}" + this.queryUrl,
                "ticket_name_field": "title",
                "mapping_field": "state.value",
                "event_list_url": "{{secret.galloper_url}}/api/v1/issues/events/{{secret.project_id}}",
                "ticket_id_field": "id",
                "event_detail_url": "{{secret.galloper_url}}/api/v1/issues/event/{{secret.project_id}}",
                "name": "board_01",
                "engagement": this.engagement,
                "columns": [
                    "NEW ISSUE",
                    "TICKET CREATION FAILED",
                    "BLOCKED",
                    "DONE"
                ]
            }
            
        }
    },
    watch: {
        queryUrl(value){
            this.defaultValues["tickets_url"] = "{{secret.galloper_url}}" + value
        },

    },
    mounted(){
        this.setBoardEvents()
    },
    methods: {
        splitColumnNames(columnsStr){
            result = []
            columns = columnsStr.split(',')
            columns.forEach(column => result.push(column.trim()))
            return result
        },
        getFormData(form_id){
            var data = $(form_id).serializeObject();
            data['columns'] = this.splitColumnNames(data['columns'])
            return data
        },
        setBoardEvents(){
            $(this.modal_id).on("show.bs.modal", () => {
                $('#form-create').get(0).reset();
                $('#input-name').val(this.defaultValues.name)
                columnsStr = this.defaultValues.columns.join()
                $('#input-columns').val(columnsStr)
                $('#input-query-url').val(this.defaultValues.tickets_url)
                $('#input-state-update-url').val(this.defaultValues.state_update_url)
                $('#input-event-list-url').val(this.defaultValues.event_list_url)
                $('#input-event-detail-url').val(this.defaultValues.event_detail_url)
                $('#input-ticket-id-field').val(this.defaultValues.ticket_id_field)
                $('#input-mapping-field').val(this.defaultValues.mapping_field)
                $('#input-ticket-name-field').val(this.defaultValues.ticket_name_field)
                setOptions("#engagement", this.engagement.hash_id)
            });

            $(this.modal_id).on("hidden.bs.modal", () => {
                clearOptions("#engagement")
                $('.selectpicker').selectpicker('deselectAll');
                $('#mapping_field option').prop('selected', false).trigger('change');
                $(this.create_modal_form_id).get(0).reset();
            });

            $("#advancedSettingsArea").on('show.bs.collapse', ()=>{
                $("#exp-icon").removeClass("icon-arrow-down__16")
                $("#exp-icon").addClass("icon-arrow-up__16")
            });

            $("#advancedSettingsArea").on('hide.bs.collapse', ()=>{
                $("#exp-icon").removeClass("icon-arrow-up__16")
                $("#exp-icon").addClass("icon-arrow-down__16")
            });

            $("#create-btn").click(() => {
                data = $(this.create_modal_form_id).serializeObject();
                axios.post(boards_url, data)
                  .then(()  => {
                    showNotify("SUCCESS", "Board created")
                    $(this.modal_id).modal("hide");
                  })
                  .catch(error => {
                    console.log(error);
                    showNotify("ERROR")
                  });
            });
        }
    },
    template: `
        <div id="board_create_modal" class="modal modal-small fixed-left fade shadow-sm" tabindex="-1" role="dialog">
            <div class="modal-dialog modal-dialog-aside" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <div class="row w-100">
                            <div class="col">
                                <h2>Create board</h2>
                            </div>
                            <div class="col-xs">
                                <button type="button" class="btn  btn-secondary mr-2" data-dismiss="modal" aria-label="Close">
                                    Cancel
                                </button>
                                <button type="button" class="btn  btn-secondary mr-2" id="save_as_template">
                                    Save as template
                                </button>
                                <button type="button" id="create-btn" class="btn btn-basic">Save</button>
                            </div>
                        </div>
                    </div>
                    <div class="modal-body">
                        <form id="board-form-create">
                            <div class="section p-1">

                                <div class="custom-input mb-3">    
                                    <label for="input-name" class="font-weight-bold mb-1">Name</label>
                                    <input type="text" name="name" id="name">
                                </div>

                                <div class="custom-input mb-3">
                                    <label for="input-mapping-field" class="font-weight-bold mb-0">Mapping field</label>
                                    <p class="custom-input_desc mb-2">Field used to sort tickets to columns</p>
                                    <select class="selectpicker bootstrap-select__b w-100-imp" data-style="btn" name="mapping_field" id="mapping_field">
                                        <option value="status">Status</option>
                                        <option value="assignee">Assignee</option>
                                        <option value="type">Type</option>
                                        <option value="state.value">State</option>
                                    </select>
                                </div>

                                <div class="custom-input mb-3">
                                    <label for="input-columns" class="font-weight-bold mb-0">Columns</label>
                                    <p class="custom-input_desc mb-2">Specify board columns</p>
                                    <select class="selectpicker bootstrap-select__b w-100-imp" data-style="btn" name="columns[]" id="columns" multiple>
                                        <option value="open">Open</option>
                                        <option value="in_progress">In progress</option>
                                        <option value="done">Done</option>
                                    </select>
                                </div>

                                <div class="custom-input mb-3">
                                    <label for="input-columns" class="font-weight-bold mb-1">Ticket card attributes</label>
                                    <select class="selectpicker bootstrap-select__b w-100-imp" data-style="btn" name="tickets_attributes[]" id="ticket_attributes" multiple>
                                        <option value="title">Title</option>
                                        <option value="assignee">Assignee</option>
                                        <option value="status">Status</option>
                                        <option value="severity">Severity</option>
                                        <option value="type">Ticket type</option>
                                        <option value="engagement">Engagement</option>
                                    </select>
                                </div>

                                <div class="custom-input mb-5">
                                    <label for="input-engagement" class="font-weight-bold mb-1">Engagement</label>
                                    <select class="selectpicker bootstrap-select__b w-100-imp" data-style="btn" name="engagement" id="engagement">
                                    </select>
                                </div>

                                <h4 class="mb-0 mt-3">ADVANCED SETTINGS
                                    <div class="d-inline-block">
                                        <a href="#advancedSettingsArea" data-toggle="collapse" aria-expanded="false" aria-controls="advancedSettingsArea">
                                            <i id="exp-icon" class="icon__16x16 icon-arrow-down__16"></i>
                                        </a>
                                    </div> 
                                </h4>
                                <p class="custom-input_desc mb-3">Advanced settings of board</p>

                                <div id="advancedSettingsArea" class="collapse">
                                    <div class="custom-input mb-3">
                                        <label for="input-query-url" class="font-weight-bold mb-1">Query Url</label>
                                        <input type="url" name="tickets_url" class="form-control board-column" id="input-query-url">
                                    </div>

                                    <div class="custom-input mb-3">
                                        <label for="input-state-update-url" class="font-weight-bold mb-1">State Update Url</label>
                                        <input type="url" name="state_update_url" class="form-control board-column" id="input-state-update-url">
                                    </div>
            
                                    <div class="custom-input mb-3">
                                        <label for="input-project" class="font-weight-bold mb-1">Event List Url</label>
                                        <input type="url" name="event_list_url" class="form-control board-column" id="input-event-list-url">
                                    </div>

                                    <div class="custom-input mb-3">
                                        <label for="input-project" class="font-weight-bold mb-1">Event Detail Url</label>
                                        <input type="url" name="event_detail_url" class="form-control board-column" id="input-event-detail-url">
                                    </div>

                                    <div class="custom-input mb-3">
                                        <label for="input-project" class="font-weight-bold mb-1">Ticket id Field</label>
                                        <input type="url" name="ticket_id_field" class="form-control board-column" id="input-ticket-id-field">
                                    </div>

                                    <div class="custom-input mb-3">
                                        <label for="input-project" class="font-weight-bold mb-1">Ticket Name Field</label>
                                        <input type="url" name="ticket_name_field" class="form-control board-column" id="input-ticket-name-field">
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <button 
            type="button" 
            class="btn-sm btn-secondary" 
            data-toggle="modal" 
            data-target="#board_create_modal"
        >
            Create board
        </button>
    `
}
