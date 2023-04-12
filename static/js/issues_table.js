const IssuesTable = {
    props: ['engagement'],
    data() {
        return {
            // table fields
            issues_url: issues_api_url,
            isAnyTicketSelected: false,
            
            // filter fields
            optionsFetched: false,
            selected_filters: [],
            types_options:[],
            source_options: [],
            tags_options: [],
            filterMap: {},
        }
    },
    watch: {
        engagement(value){
            if (value.id){
                this.filterMap['engagement'] = value.hash_id
            }
            this.refreshTable()
            this.fetchOptions()
        },
    },
    computed: {
        queryUrl(){
            params = ''
            for (const [key, value] of Object.entries(this.filterMap)) {
                if (Array.isArray(value)){
                    value.forEach(item => {
                        params += `${key}=${item}&`
                    })
                } else {
                    params += key + "=" + value + "&"
                }
            }
            query = params.slice(0, params.length-1)
            return issues_api_url + '?' + query
        },
    },
    methods: {
        // Filters methods
        applyFilter(filter, values){
            values = values.map(value => value['id'])
            this.filterMap[filter] = values
            this.refreshTable()
        },
        fetchOptions(){
            if (this.optionsFetched)
                return
            issues = this.getIssues()
            console.log(issues)
            this.types_options = this.getFilterOptions(issues, 'type')
            this.source_options = this.getFilterOptions(issues, 'source_type')
            this.tags_options = this.getTagsOptions(issues)
            console.log(this.tags_options)
            this.optionsFetched = true
        },
        removeFilter(item){
            delete this.filterMap[item]
            index = this.selected_filters.indexOf(item)
            this.selected_filters.splice(index, 1)
            this.refreshTable()
        },
        getIssues(){
            return $("#issues-table").bootstrapTable('getData');
        },
        toCapilizedCase(str){
            return str.charAt(0).toUpperCase() + str.slice(1)
        },
        getFilterOptions(issues, field){
            optsSet = new Set()
            options = []
            issues.forEach(issue => {
                value = issue[field]
                if (value){
                    if (!optsSet.has(value)){
                        optsSet.add(value)
                        options.push({
                            id: issue[field], 
                            title: this.toCapilizedCase(value)
                        })
                    }
                }
            })
            return options
        },

        getTagsOptions(issues){
            optsSet = new Set()
            options = []
            issues.forEach(issue => {
                tags = issue['tags']
                tags.forEach(tag => {
                    if (!optsSet.has(tag.id)){
                        optsSet.add(tag.id)
                        options.push({
                            id: tag.id, 
                            title: tag.tag
                        })
                    }
                })
            })
            return options
        },
        // Table methods
        refreshTable(){
            this.issues_url = this.queryUrl
            $("#issues-table").bootstrapTable("refresh", {
                url: this.issues_url
            })
        },
        deleteTickets(fileName, index) {
            $.ajax({
                url: `/api/v1/artifacts/artifact/${getSelectedProjectId()}/${this.selectedBucket.name}/${fileName}`,
                type: 'DELETE',
                success: (res) => {
                    $('#artifact-table').bootstrapTable('remove', {
                        field: '$index',
                        values: [index]
                    })
                    this.$emit('refresh', res.size);
                    showNotify('SUCCESS', 'File delete.');
                }
            });
        },
    },
    template: `
        <div class="card mt-3 mr-3 card-table-sm w-100">
            <div class="row px-4 pt-4">
                <div class="col-4">
                    <h4>Tickets</h4>   
                </div>
                <div class="col-8">
                    <div class="d-flex justify-content-end">
                        <div class="custom-input custom-input_search__sm mr-2 position-relative">
                            <input
                                id="search-bar"
                                type="text"
                                placeholder="Search">
                            <img src="/issues/static/ico/search.svg" class="icon-search position-absolute">
                        </div>
                        <button type="button" class="btn btn-basic btn-sm btn-icon__sm mr-2" data-toggle="modal" data-target="#modal-create"><i class="fas fa-plus"></i></button>
                        <div class="mr-2 ">
                            <MultiselectDropdown
                                variant="slot"
                                :list_items="['severity', 'type', 'source', 'status', 'tags']"
                                button_class="btn-sm btn-icon__sm btn-secondary"
                                @change="selected_filters = $event">
                                <template #dropdown_button><i class="fa fa-filter"></i></template>
                            </MultiselectDropdown>
                        </div>    
                        <button type="button" 
                            @click="deleteTickets"
                            :disabled="!isAnyTicketSelected"
                            class="btn btn-secondary btn-sm btn-icon__sm mr-2">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                        <button type="button" class="btn-sm btn-secondary">
                            Create board
                        </button>
                    </div>
                </div>
            </div>
            <div class="row px-4 pt-2">
                <div class="d-flex flex-wrap filter-container" id="filters-row">
                    <removable-filter
                        container_class="mr-2"
                        label="SEVERITY"
                        filter_name="severity"
                        :itemsList="[
                            {id: 'critical', title: 'Critical'},
                            {id: 'high', title: 'High'},
                            {id: 'medium', title: 'Medium'},
                            {id: 'low', title: 'Low'},
                            {id: 'info', title: 'Info'},
                        ]"
                        v-show="selected_filters.includes('severity')"
                        @filterRemoved="removeFilter"
                        @apply="applyFilter"
                    >
                    </removable-filter>

                    <removable-filter
                        label="TYPE"
                        filter_name="type"
                        container_class="mr-2"
                        :itemsList="types_options"
                        v-show="selected_filters.includes('type')"
                        @filterRemoved="removeFilter"
                        @apply="applyFilter"
                    >
                    </removable-filter>

                    <removable-filter
                        label="SOURCE"
                        filter_name="source_type"
                        container_class="mr-2"
                        :itemsList="source_options"
                        v-show="selected_filters.includes('source')"
                        @filterRemoved="removeFilter"
                        @apply="applyFilter"
                    >
                    </removable-filter>

                    <removable-filter
                        label="STATUS"
                        filter_name="status"
                        container_class="mr-2"
                        :itemsList="[
                            {id: 'open', title: 'Open'},
                            {id: 'closed', title: 'Closed'},
                        ]"
                        v-show="selected_filters.includes('status')"
                        @filterRemoved="removeFilter"
                        @apply="applyFilter"
                    >
                    </removable-filter>

                    <removable-filter
                        label="TAGS"
                        filter_name="tags"
                        container_class="mr-2"
                        :itemsList="tags_options"
                        v-show="selected_filters.includes('tags')"
                        @filterRemoved="removeFilter"
                        @apply="applyFilter"
                    >
                    </removable-filter>
                </div>
            </div>
            <div class="card-body">
                <table class="table table-borderless"
                    id="issues-table"
                    :data-url="issues_url"
                    data-toggle="table"
                    data-unique-id="id"
                    data-search="true"
                    data-search-selector="#search-bar"

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
                            <th data-field="source_type">Source</th>
                            <th data-field="status">Status</th>
                            <th data-field="tags" data-events="tagsEvents" data-formatter="tagsFormatter">Tags</th>
                            <th data-formatter="actionsFormatter" data-events="actionsEvents">Actions</th>
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