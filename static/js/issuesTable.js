const IssuesTable = {
    props: ['engagement'],
    components: {
        'board-creation-modal': BoardCreationModal,
        'ticket-creation-modal': TicketCreationModal,
        'filter-toolbar-container': FilterToolbarContainer,
        'small-issues-table': SmallIssuesTable,
        'ticket-view-container': TicketViewContainer,
    },
    data() {
        return {
            url: issues_api_url,
            issues_url: issues_api_url,
            noTicketSelected: true,
            preFilterMap: {},
            table_id: "#issues-table",
            selectedTicket: null,
            pageNumber: 1,
            maxPageCount: 1,

            all_users: [],
        }
    },
    mounted(){
        this.setTableCheckEvents()
        const $table = $(this.table_id)
        $table.on('click-row.bs.table', (e, row, $el, field) => {
            if (field != "actions"){
                this.selectedTicket = row
            }
        })

        $table.on('page-change.bs.table', (e, number) => {
            this.pageNumber = number
        })

        $table.on('load-success.bs.table', (e, data) => {
            itemsCount = data.total;
            this.maxPageCount = Math.ceil(itemsCount/10)
        })
    },  
    watch: {
        async selectedTicket(value){
            if (!value){
                await this.setUsersOptions()
            }
        },

        engagement(value){
            notAllEngagements = value.id!=-1
            const $table = $(this.table_id)
            if (notAllEngagements){
                this.preFilterMap['engagement'] = value.hash_id
                $table.bootstrapTable('hideColumn', 'engagement.name')
            } else {
                delete this.preFilterMap['engagement']
                $table.bootstrapTable('showColumn', 'engagement.name')
            }
        },
    },
    methods: {
        async setUsersOptions(){
            generateHtmlOptions = (items, idField='id', titleField='name', currentUserId=null)=>{
                result = items.reduce((acc, curr) => {
                    selected = curr[idField] == currentUserId ? "selected" : "" 
                    return acc + `<option value="${curr[idField]}" ${selected}>${curr[titleField]}</option>`
                }, '')
                return result
            }
            setOptions = (htmlText, selectId) => {
                const $select = $(selectId)
                $select.append(htmlText)
                $select.selectpicker('refresh')
                $select.selectpicker('render')
            }
            const resp = await fetchUsersAPI()
            this.all_users = resp['rows'] || []
            htmlTxt = generateHtmlOptions(this.all_users, 'id', 'name')
            setOptions(htmlTxt, '#input-assignee')
        },

        handleTicketChange(ticket){
            this.selectedTicket = ticket
            $(this.table_id).bootstrapTable("refresh")
            $('#input-ticket-start-date').val(this.selectedTicket?.start_date);
            $('#input-ticket-end-date').val(this.selectedTicket?.end_date);
        },

        // Table events
        setTableCheckEvents(){
            const $table = $(this.table_id)
            $table.on('check.bs.table', ()=>{
                this.noTicketSelected = false;
            })
            $table.on('check-all.bs.table', ()=>{
                this.noTicketSelected = false;
            })
            $table.on('check-all.bs.table', ()=>{
                this.noTicketSelected = false;
            })
            $table.on('uncheck.bs.table', ()=>{
                rows = $table.bootstrapTable('getSelections')
                this.noTicketSelected = rows.length == 0 ? true : false               
            })
            $table.on('uncheck-all.bs.table', ()=>{
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
        <div v-show="!selectedTicket" 
            class="card mt-3 mr-3 card-table-sm w-100">
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
                        v-if="!selectedTicket"
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
                    data-cache="false"
                    data-page-list="[10, 25, 50, 100]"

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
                            <th data-field="assignee.name">Assignee</th>
                            <th data-field="engagement.name">Engagement</th>
                            <th data-field="tags" data-events="tagsEvents" data-formatter="TagsFormatter.format">Tags</th>
                            <th data-field="actions" data-formatter="actionsFormatter" data-events="actionsEvents"></th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="detail-container">
                <small-issues-table
                    v-show="selectedTicket"
                    :issue="selectedTicket"
                    :engagement="engagement"
                    :pageNumber="pageNumber"
                    :maxPageCount="maxPageCount"
                    :ticket="selectedTicket"
                    @updated="handleTicketChange"
                >
                </small-issues-table>
                <ticket-view-container
                    v-if="selectedTicket"
                    ref="viewContainer"
                    :engagement="engagement"
                    :ticket="selectedTicket"
                    @updated="handleTicketChange"
                >
                </ticket-view-container>
        </div>
    `
}

register_component('issues-table', IssuesTable);
