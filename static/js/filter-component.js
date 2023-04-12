const RemovableFilter = {
    props: {
        filter_name: {
            default: 'label'
        },
        container_class: {
            default: ''
        },
        itemsList:{
            default: [...Array(5).keys()].map((item, index) => (
                { id: Math.round(Math.random() * 1000), title: `Step ${index + 1}`}
            ))
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
            this.$emit('filterRemoved', this.label.toLowerCase())
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

