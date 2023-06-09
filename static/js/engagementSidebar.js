
const EngagementsListAside = {
    emits: ['engagementSelected', 'engagementsListUpdated'],
    data() {
        return {
            engagementsTableId: "#engagement-table",
            currentEngIndex: null,
            engagementCount: 0,
            selectedEngagementRowIndex: 0,
            selectedEngagement: null,
            engagements: null,
        }
    },
    mounted() {
        this.fetchEngagements().then(data => {
            this.setStateAndEvents(data)
        })
    },
    components: {
        'engagement-creation-modal': EngagementCreationModal,
    },
    computed: {
        responsiveTableHeight() {
            return `${(window.innerHeight - 286)}px`;
        }
    },
    methods: {
        async fetchEngagements() {
            const res = await fetch (`/api/v1/engagements/engagements/${getSelectedProjectId()}`,{
                method: 'GET',
            })
            return res.json();
        },
        SET_ENGAGEMENTS(engagements){
            this.engagements = engagements
            this.$emit('engagementsListUpdated', engagements)
        },
        SET_ENGAGEMENT(engagement, index){
            this.selectedEngagement = engagement
            this.selectedEngagementRowIndex = index
            this.$emit('engagementSelected', engagement)
        },
        selectEngagement(index) {
            $('#engagement-table tbody tr').each((i, item) => {
                if(i === index) {
                    const firstRow = $(item);
                    firstRow.addClass('highlight');
                    engagement = $('#engagement-table').bootstrapTable('getData')[index];
                    this.SET_ENGAGEMENT(engagement, index)
                }
            })
        },
        setEvent(engagementList) {
            vm = this
            $('#engagement-table').on('click', 'tbody tr:not(.no-records-found)', function(){
                const selectedUniqId = parseInt(this.getAttribute('data-uniqueid'));
                for (let i=0; i<engagementList.length; i++){
                    engagement = engagementList[i]
                    if (engagement.id === selectedUniqId){
                        vm.SET_ENGAGEMENT(engagement, i)
                    }
                }
                $(this).addClass('highlight').siblings().removeClass('highlight');
            });
        },
        setStateAndEvents(data, index=0){
            engagements = data['items']
            engagements.unshift({id: -1, name:'All engagements'})
            $(this.engagementsTableId).bootstrapTable('append', engagements);
            this.SET_ENGAGEMENTS(engagements)
            this.setEvent(engagements)
            this.engagementCount = data['total'];
            if (data['total'] > index) {
                this.selectEngagement(index);
            }
        },
        refreshEngagements(){
            currentEngIndex = this.selectedEngagementRowIndex
            this.fetchEngagements().then(data => {
                $(this.engagementsTableId).bootstrapTable("removeAll")
                this.setStateAndEvents(data, currentEngIndex)
            })
        },

    },
    template: `
        <aside class="m-3 card card-table-sm" style="width: 340px">
            <div class="row px-4 pt-4">
                <div class="col-8">
                    <h4>Engagements</h4>
                </div>
                <div class="col-4">
                    <div class="d-flex justify-content-end">
                        <engagement-creation-modal
                            @added="refreshEngagements"
                        >
                        </engagement-creation-modal>
                    </div>
                </div>
            </div>
            <hr class="hr mb-0" />
            <div class="card-body" style="padding-top: 0">
                <table class="table table-borderless table-fix-thead"
                    id="engagement-table"
                    data-toggle="table"
                    data-show-header="false"
                    data-unique-id="id">
                    <thead class="thead-light bg-transparent">
                        <tr>
                            <th data-visible="false" data-field="id">index</th>
                            <th data-formatter="nameFormatter" data-field="name" class="engagement-name">NAME</th>
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

function nameFormatter(value, row){
    allEngagement = row['id'] == -1
    if(allEngagement){
        return value
    }
    txt = `<div class="pl-2"><img class="mr-2" src="/issues/static/ico/circle.svg">${value}</div>`
    return txt
}