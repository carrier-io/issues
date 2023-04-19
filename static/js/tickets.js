const Tickets = {
    components: {
        'issues-table': IssuesTable,
        'engagement-aside': EngagementsListAside,
        'engagement-card': TopEngagementCard,
    },
    data() {
        return {
            engagements: [],
            selectedEngagement: {
                id: -1,
                name: ''
            },
        }
    },
    methods: {
        updateEngagements(engagements){
            this.engagements = engagements
        },
        setSelectedEngagement(engagement){
            this.selectedEngagement = engagement
        }
    },
    template: ` 
        <main class="d-flex align-items-start justify-content-center mb-3">
            <engagement-aside
                @engagementsListUpdated="updateEngagements"
                @engagementSelected="setSelectedEngagement"
            >
            </engagement-aside>
            <div class="w-100 mr-3">
                <div v-if="selectedEngagement.id!=-1">
                    <engagement-card
                        :engagement="selectedEngagement"
                    >
                    </engagement-card>
                </div>
                <div>
                    <issues-table 
                        :engagement="selectedEngagement"
                        :engagementList="engagements">
                    </issues-table>
                </div>
            </div>
        </main>
    `
};

register_component('tickets', Tickets);


