const IssuesTable = {
    props: ['engagement', 'engagementsList'],
    components: {
        'board-creation-modal': BoardCreationModal,
        'ticket-creation-modal': TicketCreationModal,
        'filter-toolbar-container': FilterToolbarContainer,
    },
    data() {
        return {
            url: issues_api_url,
            issues_url: issues_api_url,
            noTicketSelected: true,
            preFilterMap: {},
            table_id: "#issues-table"
        }
    },
    mounted(){
        this.setTableCheckEvents()
    },  
    watch: {
        engagement(value){
            notAllEngagements = value.id!=-1
            if (notAllEngagements){
                this.preFilterMap['engagement'] = value.hash_id
                $(this.table_id).bootstrapTable('hideColumn', 'engagement')
            } else {
                delete this.preFilterMap['engagement']
                $(this.table_id).bootstrapTable('showColumn', 'engagement')
            }
        },
    },
    methods: {
        // Table events
        setTableCheckEvents(){
            $(this.table_id).on('check.bs.table', ()=>{
                this.noTicketSelected = false;
            })
            $(this.table_id).on('check-all.bs.table', ()=>{
                this.noTicketSelected = false;
            })
            $(this.table_id).on('check-all.bs.table', ()=>{
                this.noTicketSelected = false;
            })
            $(this.table_id).on('uncheck.bs.table', ()=>{
                rows = $(this.table_id).bootstrapTable('getSelections')
                this.noTicketSelected = rows.length == 0 ? true : false               
            })
            $(this.table_id).on('uncheck-all.bs.table', ()=>{
                this.noTicketSelected = true
            })
        },
        // Table methods
        refreshTable(queryUrl, reload=true){
            this.issues_url = queryUrl
            if(reload){
                $(this.table_id).bootstrapTable("refresh", {
                    url: this.issues_url
                })
            }
        },
        deleteTickets() {
            const ids_to_delete = $(this.table_id).bootstrapTable('getSelections').map(
                item => $.param({"id[]": item.id})
            ).join('&')
            const url = `${issues_api_url}?` + ids_to_delete
            fetch(url, {
                method: 'DELETE'
            }).then(response => {
                this.noTicketSelected = true
                msg = response.ok ? "Successfully deleted" : "Deletion failed"
                msgType = response.ok ? "SUCCESS" : "ERROR"
                showNotify(msgType, msg)
                this.refreshTable(this.issues_url)
            })
            .catch(error =>{
                console.log(error)
                showNotify("ERROR", "Deletion failed")
            })
        },
    },
    template: `
        <div class="card mt-3 mr-3 card-table-sm w-100">
            <filter-toolbar-container
                variant="slot"
                :url="url"
                resp_data_field="rows"
                :table_id="table_id"
                button_class="btn-sm btn-icon__sm btn-secondary"
                :list_items="['severity', 'type', 'source', 'status', 'tags']"
                :pre_filter_map="preFilterMap"
                @applyFilter="refreshTable"
            >
                <template #title>
                    <h4>Tickets</h4>  
                </template>

                <template #before>
                    <div class="custom-input custom-input_search__sm mr-2 position-relative">
                        <input
                            id="search-bar"
                            type="text"
                            placeholder="Search">
                        <img src="/issues/static/ico/search.svg" class="icon-search position-absolute">
                    </div>
                </template>
                
                <template #dropdown_button><i class="fa fa-filter"></i></template>
                
                <template #after>
                    <ticket-creation-modal
                        :engagement="engagement"
                    >
                    </ticket-creation-modal>  
                    <button type="button" 
                        @click="deleteTickets"
                        :disabled="noTicketSelected"
                        class="btn btn-secondary btn-sm btn-icon__sm mr-2">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                    <board-creation-modal
                        :queryUrl="issues_url"
                        :engagement="engagement"
                    >
                    </board-creation-modal>
                </template>

            </filter-toolbar-container>

            <div class="card-body">
                <table class="table table-borderless"
                    id="issues-table"
                    :data-url="issues_url"
                    data-toggle="table"
                    data-unique-id="id"
                    data-side-pagination="server"
                    data-pagination="true"
                    data-page-list="[10, 25, 50, 100, all]"

                    data-pagination-pre-text="<img src='/design-system/static/assets/ico/arrow_left.svg'>"
                    data-pagination-next-text="<img src='/design-system/static/assets/ico/arrow_right.svg'>"
                >
                    <thead class="thead-light">
                        <tr>
                            <th scope="col" data-checkbox="true"></th>
                            <th data-field="title" data-formatter="titleFormatter" data-width="30" data-width-unit="%">Title</th>
                            <th data-field="severity">Severity</th>
                            <th data-field="type">Type</th>
                            <th data-field="status">Status</th>
                            <th data-field="source_type">Source</th>
                            <th data-field="assignee">Assignee</th>
                            <th data-field="engagement">Engagement</th>
                            <th data-field="tags" data-events="tagsEvents" data-formatter="TagsFormatter.format">Tags</th>
                            <th data-formatter="actionsFormatter" data-events="actionsEvents"></th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>
    `
}

register_component('issues-table', IssuesTable);
