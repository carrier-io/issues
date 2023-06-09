const RemovableFilter = {
    props: {
        filter_name: {
            default: 'label'
        },
        container_class: {
            default: ''
        },
        itemsList:{
            default: []
        },
        label:{
            default: 'LABEL'
        },
        minWidth: {
            default: 'auto'
        },
        fixWidth: {
            default: false,
        }
    },
    emits: ['filterRemoved', 'apply'],
    data() {
        return {
            inputSearch: '',
            refSearchId: 'refSearchCbx'+Math.round(Math.random() * 1000),
            selectedItems: [],
            closeOnItem: true,
        }
    },
    computed: {
        foundItems() {
            return this.inputSearch ?
                this.itemsList.filter(item => item.title.toUpperCase().includes(this.inputSearch.toUpperCase())) :
                this.itemsList
        },
        isAllSelected() {
            return (this.selectedItems.length < this.itemsList.length) && this.selectedItems.length > 0
        }
    },
    watch: {
        selectedItems: function (val) {
            if (this.selectedItems.length !== this.itemsList.length) {
                this.$refs[this.refSearchId].checked = false;
            }
        }
    },
    methods: {
        handleRemove(){
            this.selectedItems = []
            this.$emit('filterRemoved', this.filter_name)
        },
        handleApply(){
            this.$emit("apply", this.filter_name, this.selectedItems)
        },
        handlerSelectAll() {
            if (this.selectedItems.length !== this.itemsList.length) {
                this.selectedItems = [...this.itemsList];
            } else {
                this.selectedItems.splice(0);
            }
        },
    },
    template: `
        <div id="complexList" class="complex-list complex-list__removable" :class="container_class">
            <button class="btn btn-select dropdown-toggle position-relative text-left d-flex align-items-center"
                :style="{ minWidth: minWidth }"
                type="button"   
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false">
                <span class="font-weight-500 mr-2">{{label}}:</span>
                <p class="d-flex mb-0"
                    :class="{'w-100': fixWidth}">
                    <span v-if="selectedItems.length === itemsList.length" class="complex-list_filled">All</span>
                    <span v-else-if="selectedItems.length > 0" class="complex-list_filled">{{ selectedItems.length }} selected</span>
                    <span v-else class="complex-list_empty">Select</span>
                    <span class="icon-times font-weight-bold d-flex align-items-center pl-2"
                        @click.stop="handleRemove">
                        <i class="fa fa-times"></i>
                    </span>
                </p>
            </button>
            <div class="dropdown-menu"
                :class="{'close-outside': closeOnItem}">
                <div v-if="itemsList.length > 4" class="px-3 pb-2 search-group">
                    <div class="custom-input custom-input_search__sm position-relative">
                        <input
                            type="text"
                            placeholder="Search"
                            v-model="inputSearch">
                        <img src="/issues/static/ico/search.svg" class="icon-search position-absolute">
                    </div>
                </div>
                <ul class="my-0">
                    <li
                        class="dropdown-item dropdown-menu_item d-flex align-items-center">
                        <label
                            class="mb-0 w-100 d-flex align-items-center custom-checkbox"
                            :class="{ 'custom-checkbox__minus': isAllSelected }">
                            <input
                                @click="handlerSelectAll"
                                :ref="refSearchId"
                                type="checkbox">
                            <span class="w-100 d-inline-block ml-3">All</span>
                        </label>
                    </li>
                    <li
                        class="dropdown-item dropdown-menu_item d-flex align-items-center"
                        v-for="item in foundItems" :key="item.id">
                        <label
                            class="mb-0 w-100 d-flex align-items-center custom-checkbox">
                            <input
                                :value="item"
                                v-model="selectedItems"
                                type="checkbox">
                            <span class="w-100 d-inline-block ml-3">{{ item.title }}</span>
                        </label>
                    </li>
                    <div class="d-flex justify-content-end p-3">
                        <button type="button" class="btn btn-secondary mr-2">Cancel</button>
                        <button class="btn btn-basic" type="submit" @click="handleApply">Apply</button>
                    </div>
                </ul>
            </div>
        </div>`
};

register_component('removable-filter', RemovableFilter)


const FilterToolbarContainer = {
    props: {
        url: {},
        resp_data_field:{
            default: 'items'
        },
        pre_filter_map: {
            default: {}
        },
        table_id: {
            type: [String],
            default:""
        },
        list_items: {
            type: [Array, String],
            default: []
        },
        pre_selected_indexes: {
            type: [Array, String],
            default: []
        },
        placeholder: {
            type: String,
            default: undefined
        },
        delimiter: {
            type: String,
            default: ','
        },
        container_class: {
            type: String,
            default: ''
        },
        button_class: {
            type: String,
            default: 'btn btn-select dropdown-toggle d-inline-flex align-items-center'
        },
        variant: {
            type: String,
            default: 'with_selected',
            validator(value) {
                // The value must match one of these strings
                return ['with_selected', 'slot'].includes(value)
            }
        },
        return_key: {
            type: [String, null],
            default: 'name',
        },
    },
    emits: ['applyFilter'],
    delimiters: ['[[', ']]'],
    data() {
        return {
            selected_filters: [],
            types_options:[],
            source_options: [],
            tags_options: [],
            filterMap: {},
        }
    },
    async mounted() {
        if (this.list_items.length > 0) {
            if (typeof this.pre_selected_indexes === 'string') {
                this.selected_filters = this.pre_selected_indexes.split(this.delimiter)
            } else {
                this.selected_filters = this.pre_selected_indexes
            }
        }
        await this.fetchOptions()
    },
    watch:{
        pre_filter_map:{
            deep: true,
            handler(value){
                this.filterMap = Object.assign(value)
                this.$emit('applyFilter', this.queryUrl)
            }
        }
    },
    computed: {
        li() {
            if (this.list_items.length > 0) {
                let listed_items
                if (typeof this.list_items === 'string') {
                    listed_items = this.list_items.split(this.delimiter)
                } else {
                    listed_items = this.list_items
                }
                return listed_items.map((i, index) => {
                    if (typeof i === 'object') {
                        return {
                            ...i,
                            name: i.name,
                            idx: index,
                        }
                    }
                    return {
                        name: i,
                        idx: index
                    }
                })
            }
            return []
        },

        queryUrl(){
            params = Object.keys(this.filterMap).map(key => {
                value = this.filterMap[key]
                if (Array.isArray(value)){
                    return value.map(
                        item => `${key}=${encodeURIComponent(item)}`
                    ).join('&')
                }
                return key + "=" + encodeURIComponent(value)
            }).join('&')
            querySign = params ? "?" : ""
            return this.url + querySign + params
        },

        canFetchOptions(){
            return (
                Object.keys(this.filterMap).length == 1 
                && 'engagement' in Object.keys(this.filterMap)
            ) || (Object.keys(this.filterMap).length == 0)
        },
    },
    methods: {
        applyFilter(filter, values){
            values = values.map(value => value['id'])
            this.filterMap[filter] = values
            this.$emit('applyFilter', this.queryUrl)
        },

        getTagsOptions(tags){
            return tags.map(tag => {
                return {
                    id: tag.id,
                    title: this.toCapilizedCase(tag.tag)
                }
            })
        },

        toCapilizedCase(str){
            return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
        },

        getFilterOptions(values){
            return values.map(value => {
                return {
                    id: value,
                    title: this.toCapilizedCase(value)
                }
            })
        },

        async getTableData(){
            const response = await axios.get(issues_filter_options, {
                params: {
                    "filter_fields": ["type", "source_type"],
                    "retrieve_options": true,
                }
            })
            return response.data
        },

        async fetchOptions(){
            if (!this.canFetchOptions){
                return
            }
            data = await this.getTableData()
            this.types_options = this.getFilterOptions(data['type'])
            this.source_options = this.getFilterOptions(data['source_type'])
            await this.fetchTags()  
        },

        removeFilter(item){
            delete this.filterMap[item]
            index = this.selected_filters.indexOf(item)
            this.selected_filters.splice(index, 1)
            this.$emit('applyFilter', this.queryUrl)
        },

        async fetchTags(){
            const response = await axios.get(tags_api)
            data = response.data
            this.tags_options = this.getTagsOptions(data['items'])
        },

        searchChangeHandler(e){
            value = e.target.value
            if (value){
                this.filterMap['search'] = value 
            } else {
                delete this.filterMap['search']
            }
            this.$emit('applyFilter', this.queryUrl)
        },

    },
    template: `
    <div class="row px-4 pt-4">
        <div class="col-4">
            <slot name="title"></slot>   
        </div>
        <div class="col-8">
            <div class="d-flex justify-content-end">
                
                <div class="custom-input custom-input_search__sm mr-2 position-relative">
                    <input
                        id="search-bar"
                        type="text"
                        @input="searchChangeHandler"
                        placeholder="Search">
                        <img src="/issues/static/ico/search.svg" class="icon-search position-absolute">
                </div>
                
                <div class="mr-2">
                    <div class="dropdown_simple-list" 
                        :class="container_class"
                    >
                        <button class="btn-sm btn-icon__sm" type="button"
                            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"
                            :class="button_class"
                        >
                            <div v-if="variant === 'slot'">
                                <slot name="dropdown_button"></slot>
                            </div>
                            <div v-else>
                                <span class="complex-list_filled" v-if="selected_filters.length > 0">
                                    [[ selected_filters.length ]] selected
                                </span>
                                <span v-else class="complex-list_empty">[[ placeholder ]]</span>
                            </div>
                        </button>
                        <ul class="dropdown-menu"
                            v-if="li.length > 0"
                            @click="$event.stopPropagation()"
                        >
                            <li class="dropdown-menu_item p-0" 
                                v-for="i in li" 
                                :key="i.idx"
                            >
                                <label class="d-flex align-items-center custom-checkbox px-3 py-2">
                                    <input
                                        :value="i.name"
                                        v-model="selected_filters"
                                        type="checkbox"
                                    >
                                    <span v-if="i.html !== undefined" v-html="i.html"></span>
                                    <span v-else class="w-100 d-inline-block ml-3">[[ i.name ]]</span>
                                </label>
                            </li>
                        </ul>
                        <div class="dropdown-menu py-0" v-else>
                            <span class="px-3 py-2 d-inline-block">Nothing to select</span>
                        </div>
                    </div>
                </div>

                <slot name="after">
                </slot>
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
    </div>
    `
}

register_component('FilterToolbarContainer', FilterToolbarContainer)