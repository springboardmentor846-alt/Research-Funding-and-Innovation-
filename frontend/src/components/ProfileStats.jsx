import { Grid } from "@mui/material";

import StatCard from "./StatCard";

function ProfileStats({ profile }) {

    return (

        <Grid
            container
            spacing={3}
        >

            <Grid size={{ xs: 12, md: 3 }}>

                <StatCard

                    title="Publications"

                    value={profile.publications}

                    color="#2563EB"

                />

            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>

                <StatCard

                    title="Patents"

                    value={profile.patents}

                    color="#16A34A"

                />

            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>

                <StatCard

                    title="Experience"

                    value={profile.experience}

                    color="#EA580C"

                />

            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>

                <StatCard

                    title="TRL"

                    value={profile.trl_level}

                    color="#7C3AED"

                />

            </Grid>

        </Grid>

    );

}

export default ProfileStats;
