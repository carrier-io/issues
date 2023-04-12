
const EngagementsListAside = {
    props: ['selectedEngagementRowIndex', 'selectedEngagement', 'engagementCount'],
    data() {
        return {
            canSelectItems: false,
        }
    },
    computed: {
        responsiveTableHeight() {
            return `${(window.innerHeight - 286)}px`;
        }
    },
    async mounted(){
        console.log(issues_api_url)
    },
    methods: {
        switchSelectItems() {
            this.canSelectItems = !this.canSelectItems;
            const action = this.canSelectItems ? 'showColumn' : 'hideColumn';
            $('#engagement-table').bootstrapTable(action, 'select');
            document.getElementById("engagement-table")
                .rows[this.selectedBucketRowIndex + 1]
                .classList.add('highlight');
        },
        setEngagementEvents() {
            const vm = this;
            $('#engagement-table').on('sort.bs.table', function () {
                vm.$nextTick(() => {
                    $('#engagement-table').find(`[data-uniqueid='${vm.selectedEngagement.id}']`).addClass('highlight');
                })
            });
        },
    },
    template: `
        <aside class="m-3 card card-table-sm" style="width: 340px">
            <div class="row p-4">
                <div class="col-8">
                    <h4>Engagements</h4>
                </div>
                <div class="col-4">
                    <div class="d-flex justify-content-end">
                        <button type="button"
                             data-toggle="modal" 
                             data-target="#CreateEngModal"
                             class="btn btn-secondary btn-sm btn-icon__sm">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
            <div class="card-body" style="padding-top: 0">
                <table class="table table-borderless table-fix-thead"
                    id="engagement-table"
                    data-toggle="table"
                    data-unique-id="id">
                    <thead class="thead-light bg-transparent">
                        <tr>
                            <th data-visible="false" data-field="id">index</th>
                            <th data-sortable="true" data-field="name" class="engagement-name">NAME</th>
                        </tr>
                    </thead>
                    <tbody :style="{'height': responsiveTableHeight}">
                    </tbody>
                </table>
                <div class="p-3">
                    <span class="font-h5 text-gray-600">{{ engagementCount }} items</span>
                </div>
            </div>
        </aside>
    `
}