import React from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Chip,
  Box,
  Divider,
  Paper
} from "@mui/material";
import policyData from "./data.json";

const InsurerDetails = policyData.InsurerDetails;
const PolicyFeatures = policyData.PolicyFeatures;

const colorScheme = {
  primary: "#d50060", // Pinkish red from the header
  good: "#43a047",   // Green for Good
  decent: "#ffa000", // Amber/Orange for Decent
  avoid: "#e53935",  // Red for Avoid
  background: "#f8fafc", // Very light gray/white
  card: "#fff",
  text: "#222"
};

// Helper function to decide color based on tag content
const getScoreColor = (tag) => {
  if (typeof tag === 'string' && tag.toLowerCase().includes("good")) return colorScheme.good;
  if (typeof tag === 'string' && tag.toLowerCase().includes("decent")) return colorScheme.decent;
  if (typeof tag === 'string' && tag.toLowerCase().includes("avoid")) return colorScheme.avoid;
  if (typeof tag === 'string' && tag.trim().toLowerCase() === 'yes') return colorScheme.good;
  if (typeof tag === 'string' && tag.trim().toLowerCase() === 'no') return colorScheme.avoid;
  return colorScheme.decent;
};

// Helper function for Offered background
const getOfferedBg = (value) => {
  if (typeof value === 'string' && value.trim().toLowerCase() === 'yes') return '#4caf50';
  if (typeof value === 'string' && value.trim().toLowerCase() === 'no') return '#f44336';
  return 'inherit';
};

function ScoreCard() {
  return (
    <Box sx={{ minHeight: "100vh", background: colorScheme.background }}>
      <AppBar position="static" sx={{ background: colorScheme.primary }}>
        <Toolbar>
          <Typography variant="h4" sx={{ flexGrow: 1, color: "#fff", fontWeight: 700 }}>
            Insurance Policy Scorecard
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 3, mb: 4, borderRadius: 3, background: colorScheme.card }}>
          <Typography variant="h5" sx={{ color: colorScheme.primary, fontWeight: 600, mb: 2 }}>
            {InsurerDetails.InsurancePolicy} by {InsurerDetails.Insurer}
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>3 Year Average CSR</strong>
              </Typography>
              <Typography>{InsurerDetails.ThreeYearAverageCSR.Value}</Typography>
              <Typography sx={{ color: getScoreColor(InsurerDetails.ThreeYearAverageCSR.Tag) }}>
                {InsurerDetails.ThreeYearAverageCSR.Tag}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>Network Hospitals</strong>
              </Typography>
              <Typography>{InsurerDetails.NetworkHospitals.Value}</Typography>
              <Typography sx={{ color: getScoreColor(InsurerDetails.NetworkHospitals.Tag) }}>
                {InsurerDetails.NetworkHospitals.Tag}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>Volume of Complaints</strong>
              </Typography>
              <Typography>{InsurerDetails.VolumeOfComplaints.Value}</Typography>
              <Typography sx={{ color: getScoreColor(InsurerDetails.VolumeOfComplaints.Tag) }}>
                {InsurerDetails.VolumeOfComplaints.Tag}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>Solvency Ratio</strong>
              </Typography>
              <Typography>{InsurerDetails.SolvencyRatio.Value}</Typography>
              <Typography sx={{ color: getScoreColor(InsurerDetails.SolvencyRatio.Tag) }}>
                {InsurerDetails.SolvencyRatio.Tag}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>Pay-Out Ratio</strong>
              </Typography>
              <Typography>{InsurerDetails.PayOutRatio.Value}</Typography>
              <Typography sx={{ color: getScoreColor(InsurerDetails.PayOutRatio.Tag) }}>
                {InsurerDetails.PayOutRatio.Tag}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>Revenue Ranking</strong>
              </Typography>
              <Typography>{InsurerDetails.RevenueRanking}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>Online Claim Tracking</strong>
              </Typography>
              <Typography>{InsurerDetails.OnlineClaimTracking}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>Cashless Settlement Time</strong>
              </Typography>
              <Typography>{InsurerDetails.AverageCashlessSettlementTime}</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle1">
                <strong>Non-Cashless Settlement Time</strong>
              </Typography>
              <Typography>{InsurerDetails.AverageNonCashlessSettlementTime}</Typography>
            </Grid>
          </Grid>
        </Paper>
        <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 3, background: colorScheme.card }}>
          <Typography variant="h6" sx={{ color: colorScheme.primary, fontWeight: 600, mb: 2 }}>
            Mandatory Features
          </Typography>
          <Grid container spacing={2}>
            {PolicyFeatures.filter(f => f.Category === "Mandatory").map((feature, idx) => (
              <Grid item xs={12} sm={6} key={idx}>
                <Card sx={{ background: colorScheme.background, borderRadius: 2, boxShadow: 1 }}>
                  <CardContent>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: colorScheme.text }}>
                      {feature.FeatureName}
                    </Typography>
                    <Chip
                      label={feature.FeatureOffered}
                      sx={{
                        backgroundColor: `${getScoreColor(feature.FeatureOffered)} !important`,
                        color: `#fff !important`,
                        fontWeight: 600,
                        ml: 1
                      }}
                    />
                    <Typography variant="body2" sx={{ mt: 1 }}>{feature.Explanation}</Typography>
                    <Typography variant="body2" sx={{ mt: 1, color: colorScheme.primary }}><b>Details:</b> {feature.Details}</Typography>
                    <Typography variant="body2" sx={{ mt: 1, color: colorScheme.avoid }}><b>Caveats:</b> {feature.Caveats}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
        <Paper elevation={2} sx={{ p: 3, borderRadius: 3, background: colorScheme.card }}>
          <Typography variant="h6" sx={{ color: colorScheme.primary, fontWeight: 600, mb: 2 }}>
            Good To Have Features
          </Typography>
          <Grid container spacing={2}>
            {PolicyFeatures.filter(f => f.Category !== "Mandatory").map((feature, idx) => (
              <Grid item xs={12} sm={6} key={idx}>
                <Card sx={{ background: colorScheme.background, borderRadius: 2, boxShadow: 1 }}>
                  <CardContent>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, color: colorScheme.text }}>
                      {feature.FeatureName}
                    </Typography>
                    <Chip
                      label={feature.FeatureOffered}
                      sx={{
                        backgroundColor: `${getScoreColor(feature.FeatureOffered)} !important`,
                        color: `#fff !important`,
                        fontWeight: 600,
                        ml: 1
                      }}
                    />
                    <Typography variant="body2" sx={{ mt: 1 }}>{feature.Explanation}</Typography>
                    <Typography variant="body2" sx={{ mt: 1, color: colorScheme.primary }}><b>Details:</b> {feature.Details}</Typography>
                    <Typography variant="body2" sx={{ mt: 1, color: colorScheme.avoid }}><b>Caveats:</b> {feature.Caveats}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
}

export default ScoreCard;